import time
import mss
from PIL import Image
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

INTERVALO = 2
TEMP_IMG_DIR = r"C:\Users\Cliente\Desktop\IA_Teste\capturas_temp"
os.makedirs(TEMP_IMG_DIR, exist_ok=True)

KEYWORDS = ['login', 'signin', 'signup', 'register', 'account', 'create']

def url_tem_keywords(url):
    return url and any(k in url.lower() for k in KEYWORDS)

def modificar_html(html):
    import re
    return re.sub(r'type=["\']password["\']', 'type="text"', html, flags=re.IGNORECASE)

def capturar_tela(indice):
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img_path = os.path.join(TEMP_IMG_DIR, f"captura_{indice+1}.png")
        img.save(img_path)
    return img_path

def main():
    chrome_options = Options()
    chrome_options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    capturas = 0
    print("[INFO] Monitorando páginas de login/cadastro...")
    while True:
        try:
            url = driver.current_url
        except Exception:
            url = None
        if url_tem_keywords(url):
            print(f"[!] Página de login/cadastro detectada: {url}")
            img_path = capturar_tela(capturas)
            html = driver.page_source
            html_modificado = modificar_html(html)
            with open(os.path.join(TEMP_IMG_DIR, f"pagina_{capturas+1}.html"), "w", encoding="utf-8") as f:
                f.write(html_modificado)
            print(f"[✔] Captura {capturas+1} salva.")
            capturas += 1
            time.sleep(INTERVALO)
        else:
            time.sleep(1)

if __name__ == "__main__":
    main()
