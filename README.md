# MikoProject

\# Miko AI Pentest Scanner



An automated penetration testing tool with a graphical user interface (GUI), designed to scan websites and generate security reports using local AI.



\## Features

\*   \*\*Port Scanning:\*\* Uses Nmap to find open ports and services.

\*   \*\*Vulnerability Scanning:\*\* Integrates OWASP ZAP to detect web vulnerabilities (SQLi, XSS, etc.).

\*   \*\*Weak Password Check:\*\* Tests login forms against a dictionary of common passwords.

\*   \*\*AI Reporting:\*\* Uses local LLM (via Ollama) to analyze the raw scan data and generate a human-readable security report in Russian.

\*   \*\*Modern GUI:\*\* Built with Python and Tkinter, featuring a dark theme and custom avatar.



\## Tech Stack

\*   Python 3

\*   Tkinter (GUI)

\*   Nmap \& OWASP ZAP (Scanning engines)

\*   Ollama (Local AI - Qwen model)



\## How to run

1\. Make sure you have Nmap, OWASP ZAP, and Ollama installed and running.

2\. Install dependencies: `pip install python-nmap openai requests python-owasp-zap-v2.4 pillow`

3\. Run the script: `python kimo.py`



\*Disclaimer: This tool is created for educational purposes and authorized penetration testing only. Do not use it on websites without permission.\*



Note: This project was developed by a 15-year-old student from Russia as a first step into cybersecurity.

