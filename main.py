import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------
# Cargar variables del entorno
# -------------------------------
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
LAB_URL = os.getenv("LAB_URL")

# -------------------------------
# Configurar Selenium
# -------------------------------
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")   # comenta para ver navegador
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), 
    options=options
)

def log(msg, status="info", depth=0):
    icons = {"ok": "✅", "info": "🔎", "wait": "⏳", "error": "❌", "done": "🚀"}
    print(f"{'  '*depth}{icons.get(status,'ℹ️')} {msg}")

def find_and_click_start_lab(driver, wait, depth=0):
    """
    Busca el botón Start Lab en el DOM actual y lo clickea si lo encuentra.
    Recorre recursivamente todos los iframes.
    """
    try:
        start_lab = wait.until(EC.presence_of_element_located((By.ID, "launchclabsbtn")))
        driver.execute_script("arguments[0].click();", start_lab)
        log(f"Botón Start Lab encontrado y clickeado en nivel {depth}", "ok", depth)
        return True
    except:
        # No está en este nivel → buscar en iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        log(f"Buscando en {len(iframes)} iframes (nivel {depth})...", "info", depth)
        for idx, iframe in enumerate(iframes):
            driver.switch_to.frame(iframe)
            found = find_and_click_start_lab(driver, wait, depth+1)
            driver.switch_to.parent_frame()
            if found:
                return True
        return False

try:
    wait = WebDriverWait(driver, 20)

    # 1. Login
    log("Abriendo página de login...", "wait")
    driver.get("https://awsacademy.instructure.com/login/canvas")

    log("Ingresando credenciales...", "wait")
    wait.until(EC.presence_of_element_located((By.ID, "pseudonym_session_unique_id"))).send_keys(EMAIL)
    driver.find_element(By.ID, "pseudonym_session_password").send_keys(PASSWORD)
    driver.find_element(By.CLASS_NAME, "Button--login").click()
    log("Login exitoso", "ok")

    # 2. Ir al lab
    log("Entrando al laboratorio...", "wait")
    driver.get(LAB_URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    log("Página del lab cargada", "ok")

    # 3. Buscar y clickear el botón Start Lab
    if not find_and_click_start_lab(driver, wait):
        raise Exception("No se encontró el botón Start Lab en ningún lugar")

    # 4. Esperar redirección a la consola AWS
    log("Esperando redirección a la consola AWS...", "wait")
    wait.until(lambda d: "console.aws.amazon.com" in d.current_url or "awsacademy.instructure.com" in d.current_url)

    aws_console_url = driver.current_url
    log(f"Consola AWS lista en: {aws_console_url}", "done")

except Exception as e:
    log(f"Error: {e}", "error")

finally:
    driver.quit()
