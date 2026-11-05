import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import nmap
from openai import OpenAI
import time
import requests
import datetime
import subprocess
from PIL import Image, ImageTk
from zapv2 import ZAPv2

# --- 1. НАСТРОЙКИ ---
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL_NAME = "qwen2.5:3b"
ZAP_PATH = r"C:\Program Files\ZAP\Zed Attack Proxy\zap.bat" 

# --- 2. ЛОГИКА (ФУНКЦИИ) ---
def start_zap():
    log_web("[*] Проверяю ZAP...\n")
    try:
        requests.get("http://127.0.0.1:8080", timeout=2)
        log_web("[*] ZAP уже работает.\n")
    except requests.exceptions.ConnectionError:
        log_web("[*] Запускаю ZAP в фоне (15 сек)...\n")
        subprocess.Popen([ZAP_PATH, "-daemon", "-port", "8080"], creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(15)

def generate_report(target, nmap_results, zap_results, pass_results):
    log_web("[*] Нейросеть анализирует данные...\n")
    prompt = f"""
    Ты — опытный пентестер. Напиши отчет.
    Цель: {target}
    Nmap: {nmap_results}
    ZAP: {zap_results}
    Пароли: {pass_results}
    Структура: 1. Резюме. 2. Уязвимости. 3. Рекомендации.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": "Ты эксперт по ИБ."}, {"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка ИИ: {e}"

# --- 3. ВКЛАДКА 1: WEB PENTEST ---
def run_web_scan():
    target = entry_target.get().strip()
    if not target: return
    
    log_web(f"=== СКАНИРОВАНИЕ {target} ===\n")
    btn_web.config(state=tk.DISABLED, text="Сканирую...")

    def thread():
        start_zap()
        
        # Nmap
        log_web("[*] Nmap сканирует порты...\n")
        nm = nmap.PortScanner(nmap_search_path=[r"C:\Program Files (x86)\Nmap\nmap.exe"])
        try:
            nm.scan(hosts=target, arguments='-sV -F')
            nmap_data = str(nm.all_hosts())
        except Exception as e:
            nmap_data = f"Ошибка Nmap: {e}"
        
        # ZAP
        log_web("[*] ZAP ищет уязвимости...\n")
        zap = ZAPv2(proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'})
        if not target.startswith("http"): target = "http://" + target
        try:
            zap.spider.scan(target)
            time.sleep(5) # Для теста
            alerts = zap.core.alerts(baseurl=target)
            zap_data = str(alerts[:3]) if alerts else "Уязвимостей нет."
        except Exception as e:
            zap_data = f"Ошибка ZAP: {e}"
            
        # Пароли (упрощенно)
        pass_data = "Проверка паролей (заглушка)."

        # ИИ
        report = generate_report(target, nmap_data, zap_data, pass_data)
        log_web("\n" + "="*40 + "\n" + report)
        
        btn_web.config(state=tk.NORMAL, text="Запустить Web Scan")

    threading.Thread(target=thread, daemon=True).start()

# --- 4. ВКЛАДКА 2: OSINT (SHERLOCK) ---
def run_osint():
    username = entry_osint.get().strip()
    if not username: return
    
    log_osint(f"=== ПОИСК НИКНЕЙМА: {username} ===\n")
    btn_osint.config(state=tk.DISABLED, text="Ищу...")

    def thread():
        # В реальности тут нужно вызывать Sherlock через subprocess
        # Для теста имитируем работу
        log_osint(f"[*] Запускаю Sherlock для {username}...\n")
        time.sleep(3) 
        
        # Фейковый вывод для демонстрации
        fake_result = f"""
        [+] Найдено совпадение: https://github.com/{username}
        [+] Найдено совпадение: https://www.instagram.com/{username}
        [+] Найдено совпадение: https://vk.com/{username}
        """
        log_osint(fake_result)
        log_osint("[*] Поиск завершен.\n")
        
        btn_osint.config(state=tk.NORMAL, text="Найти никнейм")

    threading.Thread(target=thread, daemon=True).start()

# --- 5. ВКЛАДКА 3: BRUTE FORCE ---

def run_brute():
    url = entry_brute_url.get().strip()
    login = entry_brute_login.get().strip()
    
    if not url or not login: return

    log_brute(f"=== ПОДБОР ПАРОЛЯ ДЛЯ {login} ===\n")
    btn_brute.config(state=tk.DISABLED, text="Подбираю...")

    def thread():
        try:
            with open("passwords.txt", "r", encoding="utf-8") as f:
                passwords = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            log_brute("[-] Ошибка: Файл passwords.txt не найден.\n")
            btn_brute.config(state=tk.NORMAL, text="Запустить Brute Force")
            return

        log_brute(f"[*] Загружено {len(passwords)} паролей.\n")
        
        # Имитация подбора (чтобы не забанили)
        for pwd in passwords[:5]:
            log_brute(f"[*] Пробую: {pwd}...\n")
            time.sleep(1) # Задержка для эффекта
            if pwd == "admin":
                log_brute(f"[+] УСПЕХ! Пароль найден: {pwd}\n")
                break
        else:
            log_brute("[-] Пароль не найден в словаре.\n")

        btn_brute.config(state=tk.NORMAL, text="Запустить Brute Force")

    threading.Thread(target=thread, daemon=True).start()


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ЛОГОВ ---
def log_web(msg):
    log_area_web.config(state=tk.NORMAL)
    log_area_web.insert(tk.END, msg)
    log_area_web.see(tk.END)
    log_area_web.config(state=tk.DISABLED)

def log_osint(msg):
    log_area_osint.config(state=tk.NORMAL)
    log_area_osint.insert(tk.END, msg)
    log_area_osint.see(tk.END)
    log_area_osint.config(state=tk.DISABLED)

def log_brute(msg):
    log_area_brute.config(state=tk.NORMAL)
    log_area_brute.insert(tk.END, msg)
    log_area_brute.see(tk.END)
    log_area_brute.config(state=tk.DISABLED)


# --- 6. ГРАФИЧЕСКИЙ ИНТЕРФЕЙС ---
root = tk.Tk()
root.title("Miko AI Pentest - Pro Version")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

# Левая панель с Мику
try:
    avatar_img = Image.open("miko_avatar.png").resize((220, 350))
    avatar_photo = ImageTk.PhotoImage(avatar_img)
    avatar_label = tk.Label(root, image=avatar_photo, bg="#1e1e1e")
    avatar_label.place(x=20, y=100)
except:
    pass

# Главный контейнер для вкладок
style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
style.configure("TNotebook.Tab", background="#2b2b2b", foreground="#e0e0e0", padding=[10, 5])
style.map("TNotebook.Tab", background=[("selected", "#42a994")], foreground=[("selected", "black")])

notebook = ttk.Notebook(root)
notebook.place(x=260, y=20, width=720, height=660)

# --- Вкладка 1: Web Pentest ---
tab_web = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(tab_web, text="Web Pentest")

tk.Label(tab_web, text="Цель (IP или домен):", bg="#1e1e1e", fg="#e0e0e0", font=("Arial", 12)).place(x=20, y=20)
entry_target = tk.Entry(tab_web, width=30, font=("Arial", 12))
entry_target.place(x=180, y=20)
entry_target.insert(0, "testphp.vulnweb.com")

btn_web = tk.Button(tab_web, text="Запустить Web Scan", command=run_web_scan, bg="#00ffcc", fg="black", font=("Arial", 11, "bold"))
btn_web.place(x=450, y=15)

log_area_web = scrolledtext.ScrolledText(tab_web, wrap=tk.WORD, bg="#2b2b2b", fg="#e0e0e0", font=("Consolas", 10))
log_area_web.place(x=20, y=60, width=680, height=550)
log_area_web.config(state=tk.DISABLED)

# --- Вкладка 2: OSINT (Sherlock) ---
tab_osint = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(tab_osint, text="OSINT (Sherlock)")

tk.Label(tab_osint, text="Поиск по никнеймам скоро будет доступен!", 
         bg="#1e1e1e", fg="#00ffcc", font=("Arial", 16, "bold")).place(x=180, y=200)

tk.Label(tab_osint, text="Модуль находится в активной разработке.", 
         bg="#1e1e1e", fg="#e0e0e0", font=("Arial", 12)).place(x=200, y=240)

btn_osint = tk.Button(tab_osint, text="Найти никнейм (В разработке)", 
                      state=tk.DISABLED, bg="#555555", fg="#aaaaaa", font=("Arial", 11, "bold"))
btn_osint.place(x=250, y=300)

# --- Вкладка 3: Brute Force ---
tab_brute = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(tab_brute, text="Brute Force")

# Заглушка "В разработке"
tk.Label(tab_brute, text="Данный модуль находится в разработке...", 
         bg="#1e1e1e", fg="#ff5555", font=("Arial", 16, "bold")).place(x=150, y=200)

tk.Label(tab_brute, text="Скоро здесь появится возможность подбора паролей по словарю.", 
         bg="#1e1e1e", fg="#e0e0e0", font=("Arial", 12)).place(x=100, y=240)

# Оставляем кнопку, но делаем её неактивной (state=tk.DISABLED)
btn_brute = tk.Button(tab_brute, text="Запустить Brute Force (В разработке)", 
                      state=tk.DISABLED, bg="#555555", fg="#aaaaaa", font=("Arial", 11, "bold"))
btn_brute.place(x=250, y=300)

def on_cloing():
    root.destroy()
root.protocol("WM_DELETE_WINDOW",on_cloing)
root.mainloop()