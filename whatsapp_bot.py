import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import random
import os
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox


def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def find_browser():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            return "chrome", path
    
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in edge_paths:
        if os.path.exists(path):
            return "edge", path
    
    return None, None


class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.running = False
        self.base_path = get_base_path()
        
        self.root = tk.Tk()
        self.login_ready = tk.BooleanVar(value=False)
        self.root.title("WhatsApp Bot - Disparo Automatico")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        frame_top = tk.Frame(self.root, padx=10, pady=10)
        frame_top.pack(fill=tk.X)
        
        tk.Label(frame_top, text="Mensagem:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.msg_text = scrolledtext.ScrolledText(frame_top, height=4, width=50)
        self.msg_text.pack(fill=tk.X, pady=(0, 10))
        
        msg_file = os.path.join(self.base_path, 'mensagem.txt')
        if os.path.exists(msg_file):
            with open(msg_file, 'r', encoding='utf-8') as f:
                self.msg_text.insert(tk.END, f.read().strip())
        
        tk.Label(frame_top, text="Contatos:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.contacts_text = scrolledtext.ScrolledText(frame_top, height=3, width=50)
        self.contacts_text.pack(fill=tk.X, pady=(0, 10))
        
        contacts_file = os.path.join(self.base_path, 'contatos.txt')
        if os.path.exists(contacts_file):
            with open(contacts_file, 'r', encoding='utf-8') as f:
                self.contacts_text.insert(tk.END, f.read())
        
        frame_btn = tk.Frame(self.root, padx=10, pady=5)
        frame_btn.pack(fill=tk.X)
        
        self.btn_start = tk.Button(frame_btn, text="INICIAR", command=self.start_bot, 
                                    bg="#25D366", fg="white", font=("Arial", 12, "bold"),
                                    width=15, height=2)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_stop = tk.Button(frame_btn, text="PARAR", command=self.stop_bot,
                                   bg="#FF0000", fg="white", font=("Arial", 12, "bold"),
                                   width=15, height=2, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)
        
        self.btn_login = tk.Button(frame_btn, text="JA LOGUEI", command=self.confirm_login,
                                    bg="#075E54", fg="white", font=("Arial", 12, "bold"),
                                    width=15, height=2, state=tk.DISABLED)
        self.btn_login.pack(side=tk.LEFT)
        
        frame_log = tk.Frame(self.root, padx=10, pady=5)
        frame_log.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame_log, text="Log:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(frame_log, height=8, width=50, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_bot(self):
        msg = self.msg_text.get("1.0", tk.END).strip()
        contacts_raw = self.contacts_text.get("1.0", tk.END).strip()
        
        if not msg:
            messagebox.showerror("Erro", "Digite a mensagem!")
            return
        
        contacts = [c.strip() for c in contacts_raw.split('\n') if c.strip()]
        if not contacts:
            messagebox.showerror("Erro", "Adicione pelo menos 1 contato!")
            return
        
        self.running = True
        self.login_ready.set(False)
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_login.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self.run_bot, args=(contacts, msg), daemon=True)
        thread.start()
    
    def stop_bot(self):
        self.running = False
        self.log("Parando bot...")
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_login.config(state=tk.DISABLED)
    
    def confirm_login(self):
        self.login_ready.set(True)
        self.btn_login.config(state=tk.DISABLED)
    
    def run_bot(self, contacts, message):
        try:
            browser_type, browser_path = find_browser()
            
            if browser_type is None:
                self.log("ERRO: Nenhum navegador encontrado!")
                self.log("Instale Chrome ou Edge.")
                return
            
            self.log(f"Navegador: {browser_type.upper()}")
            self.log("Iniciando navegador...")
            
            if browser_type == "chrome":
                options = uc.ChromeOptions()
                options.add_argument("--start-maximized")
                options.add_argument("--disable-notifications")
                self.driver = uc.Chrome(options=options)
            else:
                options = EdgeOptions()
                options.add_argument("--start-maximized")
                options.add_argument("--disable-notifications")
                options.binary_location = browser_path
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=options)
            
            self.log("Abrindo WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            self.log("")
            self.log("=== ESCANEIE O QR CODE ===")
            self.log("1. Abra WhatsApp no celular")
            self.log("2. Va em Configuracoes > Aparelhos conectados")
            self.log("3. Clique em Conectar aparelho")
            self.log("4. Escaneie o QR Code que aparece no navegador")
            self.log("")
            self.log("Aguardando voce escanear...")
            self.log("(Clique JA LOGUEI quando terminar)")
            
            self.root.wait_variable(self.login_ready)
            
            self.log(f"Enviando para {len(contacts)} contatos...")
            
            for i, phone in enumerate(contacts, 1):
                if not self.running:
                    self.log("Bot parado pelo usuario.")
                    break
                
                self.log(f"[{i}/{len(contacts)}] {phone}...")
                
                try:
                    url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
                    self.driver.get(url)
                    
                    wait = WebDriverWait(self.driver, 60)
                    send_btn = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                    )
                    time.sleep(random.uniform(0.5, 1.5))
                    send_btn.click()
                    time.sleep(random.uniform(1, 2))
                    
                    self.log(f"  OK!")
                except Exception as e:
                    self.log(f"  Erro: {e}")
                
                if i < len(contacts) and self.running:
                    delay = random.uniform(120, 300)
                    self.log(f"  Aguardando {delay/60:.1f} min...")
                    
                    waited = 0
                    while waited < delay and self.running:
                        time.sleep(1)
                        waited += 1
            
            self.log("Disparo concluido!")
            
        except Exception as e:
            self.log(f"Erro: {e}")
        finally:
            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.btn_login.config(state=tk.DISABLED)
            self.running = False
    
    def on_close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.root.destroy()


if __name__ == "__main__":
    WhatsAppBot()
