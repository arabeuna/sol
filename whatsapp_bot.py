import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import sys
import traceback


def load_contacts(filepath):
    contacts = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                contacts.append(line)
    return contacts


def load_message(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def random_delay(min_minutes=2, max_minutes=5):
    delay = random.uniform(min_minutes * 60, max_minutes * 60)
    print(f"Aguardando {delay/60:.1f} minutos...")
    time.sleep(delay)


def send_whatsapp_message(driver, phone, message):
    try:
        url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
        driver.get(url)

        wait = WebDriverWait(driver, 60)

        send_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        )
        time.sleep(random.uniform(0.5, 1.5))
        send_btn.click()

        time.sleep(random.uniform(1, 2))
        print(f"  Mensagem enviada para {phone}")
        return True
    except Exception as e:
        print(f"  Erro ao enviar para {phone}: {e}")
        return False


def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def main():
    base_path = get_base_path()
    contacts_file = os.path.join(base_path, 'contatos.txt')
    message_file = os.path.join(base_path, 'mensagem.txt')

    if not os.path.exists(contacts_file):
        print(f"Arquivo {contacts_file} nao encontrado.")
        pause()
        return

    if not os.path.exists(message_file):
        print(f"Arquivo {message_file} nao encontrado.")
        pause()
        return

    contacts = load_contacts(contacts_file)
    message = load_message(message_file)

    print(f"Carregados {len(contacts)} contatos.")
    print(f"Mensagem: {message[:50]}...")
    print()

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    driver = uc.Chrome(options=options)

    try:
        print("Abrindo WhatsApp Web...")
        driver.get("https://web.whatsapp.com")

        print("Escaneie o QR Code com seu celular...")
        print("Pressione ENTER quando estiver logado...")
        pause()

        print(f"\nIniciando disparo para {len(contacts)} contatos...\n")

        for i, phone in enumerate(contacts, 1):
            print(f"[{i}/{len(contacts)}] Enviando para {phone}...")
            send_whatsapp_message(driver, phone, message)

            if i < len(contacts):
                random_delay(2, 5)

        print("\nDisparo concluido!")

    except Exception as e:
        print(f"\nErro: {e}")
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass

    pause()


def pause():
    print("\nPressione ENTER para continuar...")
    try:
        input()
    except EOFError:
        time.sleep(999999)


if __name__ == "__main__":
    main()
