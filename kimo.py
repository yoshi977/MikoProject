import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import nmap
from openai import OpenAI
import time
import requests
from PIL import Image, ImageTk
from zapv2 import ZAPv2
import subprocess
import os

# --- 1. НАСТРОЙКИ ---
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
MODEL_NAME = "qwen2.5:3b"

# Путь к ZAP (проверь, совпадает ли он у тебя)
ZAP_PATH = r"C:\Program Files\ZAP\Zed Attack Proxy\zap.bat"

# --- 2. АВТОЗАПУСК ZAP ---
def start_zap():
    update_log("[*] Проверяю, запущен ли ZAP...\n")
    try:
        # Пытаемся подключиться к ZAP
        zap = ZAPv2(proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'})
        zap.core.version
        update_log("[+] ZAP уже работает!\n")
        return True
    except:
        update_log("[*] ZAP не найден. Запускаю в фоне (подожди 15 сек)...\n")
        try:
            # Запускаем ZAP без открытия окна
            subprocess.Popen([ZAP_PATH, "-daemon", "-port", "8080"],
                             creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(15) # Ждем загрузки ZAP
            return True
        except Exception as e:
            update_log(f"[!] Ошибка запуска ZAP: {e}\n")
            return False

# --- 3. ФУНКЦИИ СКАНИРОВАНИЯ ---
def scan_ports(target):
    update_log(f"[*] Запускаю Nmap для {target}...\n")
    nm = nmap.PortScanner()
    try:
        nm.scan(hosts=target, arguments='-sV -F')
        results = ""
        for host in nm.all_hosts():
            results += f"Хост: {host}\n"
            for proto in nm[host].all_protocols():
                ports = nm[host][proto].keys()
                for port in ports:
                    state = nm[host][proto][port]['state']
                    service = nm[host][proto][port]['name']
                    results += f"  Порт {port}/{proto}: {state} ({service})\n"
        if not results:
            return "Nmap не нашел открытых портов."
        return results
    except Exception as e:
        return f"Ошибка Nmap: {e}"

def scan_zap(target):
    update_log(f"[*] Подключаюсь к ZAP для {target}...\n")
    zap = ZAPv2(proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'})
 
    if not target.startswith("http"):
        target = "http://" + target

    try:
        zap.urlopen(target)
        time.sleep(2)
 
        update_log("[*] ZAP: Ищу страницы на сайте (Spider)...\n")
        scan_id = zap.spider.scan(target)
        while int(zap.spider.status(scan_id)) < 100:
            time.sleep(2)
 
        update_log("[*] ZAP: Проверяю уязвимости (Active Scan)...\n")
        scan_id = zap.ascan.scan(target)
        while int(zap.ascan.status(scan_id)) < 100:
            time.sleep(3)
 
        alerts = zap.core.alerts(baseurl=target)
 
        if not alerts:
            return "ZAP не нашел уязвимостей."
 
        report = ""
        for alert in alerts:
            report += f"Уязвимость: {alert['alert']}\n"
            report += f"  Риск: {alert['risk']}\n"
            report += f"  URL: {alert['url']}\n"
        return report
    except Exception as e:
        return f"Ошибка ZAP: {e}"

def check_weak_passwords(target_url, username="admin"):
    update_log(f"[*] Проверяю слабые пароли на {target_url}...\n")
    if not target_url.startswith("http"):
        target_url = "http://" + target_url

    try:
        with open("passwords.txt", "r", encoding="utf-8") as f:
            passwords = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return "Ошибка: Файл passwords.txt не найден."

    passwords = passwords[:10]
    found = []
 
    for pwd in passwords:
        data = {"username": username, "password": pwd}
        try:
            response = requests.post(target_url, data=data, timeout=3)
            if "Welcome" in response.text or response.status_code == 302:
                found.append(pwd)
                break
        except requests.exceptions.RequestException:
            pass

    if found:
        return f"КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: Найден слабый пароль '{found[0]}' для пользователя {username}."
    return "Проверка паролей пройдена. Слабых паролей из топ-10 не найдено."

# --- 4. НЕЙРОСЕТЬ ---
def generate_report(target, nmap_results, zap_results, pass_results):
    update_log("[*] Отправляю данные нейросети для анализа... (это может занять время)\n")
 
    prompt = f"""
    Ты — опытный пентестер. Твоя задача — написать отчет для клиента.
    Цель: {target}
 
    Результаты Nmap (открытые порты):
    {nmap_results}
 
    Результаты ZAP (веб-уязвимости):
    {zap_results}
 
    Результаты проверки паролей:
    {pass_results}
 
    Напиши отчет по структуре:
    1. Резюме (насколько безопасна цель).
    2. Найденные уязвимости (объясни простым языком, чем они опасны).
    3. Рекомендации по исправлению.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Ты — эксперт по кибербезопасности. Пиши четко и по делу на русском языке."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка нейросети: {e}"

# --- 5. ЛОГИКА ИНТЕРФЕЙСА ---
def update_log(message):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, message)
    chat_area.see(tk.END)
    chat_area.config(state=tk.DISABLED)

def run_scan():
    target = entry_target.get().strip()
    if not target:
        messagebox.showwarning("Ошибка", "Введите IP-адрес или домен!")
        return
 
    chat_area.config(state=tk.NORMAL)
    chat_area.delete(1.0, tk.END)
    chat_area.config(state=tk.DISABLED)
 
    btn_start.config(state=tk.DISABLED, text="Сканирую...")
 
    def scan_thread():
        update_log(f"=== НАЧАЛО СКАНИРОВАНИЯ {target} ===\n")
 
        # Автозапуск ZAP
        if not start_zap():
            update_log("[!] Сканирование ZAP будет пропущено.\n")
            zap_data = "ZAP не запущен."
        else:
            zap_data = scan_zap(target)
 
        nmap_data = scan_ports(target)
        pass_data = check_weak_passwords(target)
 
        report = generate_report(target, nmap_data, zap_data, pass_data)
 
        update_log("\n" + "="*40 + "\n")
        update_log("ОТЧЕТ ДЛЯ КЛИЕНТА:\n")
        update_log("="*40 + "\n")
        update_log(report + "\n")
 
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report)
        update_log("\n[*] Отчет также сохранен в файл report.md\n")
 
        btn_start.config(state=tk.NORMAL, text="Запустить сканирование")
 
    threading.Thread(target=scan_thread, daemon=True).start()

# --- 6. ОКНО (ИНТЕРФЕЙС) ---
root = tk.Tk()
root.title("Miko AI Pentest")
root.geometry("900x650")
root.configure(bg="#1e1e1e")

# Загрузка картинки (просто имя файла, без путей)
try:
    avatar_img = Image.open("miko_avatar.png")
    avatar_img = avatar_img.resize((220, 350))
    avatar_photo = ImageTk.PhotoImage(avatar_img)
    avatar_label = tk.Label(root, image=avatar_photo, bg="#1e1e1e")
    avatar_label.place(x=20, y=150)
except Exception as e:
    print(f"Картинка не найдена: {e}")

# Правая панель
right_frame = tk.Frame(root, bg="#1e1e1e")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(260, 20), pady=10)

title_label = tk.Label(right_frame, text="Miko AI Pentest Scanner", font=("Arial", 18, "bold"), bg="#1e1e1e", fg="#00ffcc")
title_label.pack(pady=(0, 15))

frame_target = tk.Frame(right_frame, bg="#1e1e1e")
frame_target.pack(pady=5, fill=tk.X)

tk.Label(frame_target, text="Цель:", bg="#1e1e1e", fg="#e0e0e0", font=("Arial", 12)).pack(side=tk.LEFT)
entry_target = tk.Entry(frame_target, width=35, font=("Arial", 12))
entry_target.pack(side=tk.LEFT, padx=10)
entry_target.insert(0, "127.0.0.1")

btn_start = tk.Button(right_frame, text="Запустить сканирование", command=run_scan, bg="#00ffcc", fg="black", font=("Arial", 12, "bold"))
btn_start.pack(pady=15)

chat_area = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, bg="#2b2b2b", fg="#e0e0e0", font=("Consolas", 10))
chat_area.pack(pady=5, fill=tk.BOTH, expand=True)
chat_area.config(state=tk.DISABLED)

root.mainloop()