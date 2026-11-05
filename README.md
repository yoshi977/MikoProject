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


## Installation & Usage

Because this tool relies on external security scanners and local AI, please ensure you have the following prerequisites installed on your system before running the script.

### Prerequisites (What you need to install)

1. **Python 3.10+** (Make sure to check "Add Python to PATH" during installation).
2. **Nmap:** Download and install from [nmap.org](https://nmap.org/download.html). *Important: Ensure the Nmap path is added to your system's Environment Variables.*
3. **Java (JDK 17 or higher):** Required to run OWASP ZAP. Download from [Adoptium](https://adoptium.net/).
4. **OWASP ZAP:** Download and install from [zaproxy.org](https://www.zaproxy.org/download/).
5. **Ollama:** Download from [ollama.com](https://ollama.com/).

### Step-by-Step Setup

**1. Install Python dependencies**
Open your terminal (or command prompt) and run this command:
```bash
**pip install python-nmap openai requests python-owasp-zap-v2.4 pillow**

**2. Download the AI model**
Make sure Ollama is running in the background, then open a terminal and download the model:
**ollama pull qwen2.5:3b**

**3. Prepare the configuration**
* Create a file named passwords.txt in the same folder as kimo.py and add a list of common passwords (one per line).
* Place your avatar image named miko_avatar.png in the same folder.

**4. Run the application**
Open a terminal in the project folder and run:
**python kimo.py**

*Note: The application will automatically start OWASP ZAP in the background (daemon mode) on port 8080 when you click "Start Scan".*




Note: This project was developed by a 15-year-old student from Russia as a first step into cybersecurity.

