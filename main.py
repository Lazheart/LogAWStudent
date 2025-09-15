import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
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
options.add_argument("--headless=new")  # Headless moderno
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-logging")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Bloquear imágenes y fuentes para acelerar
def block_heavy_resources(driver: WebDriver):
    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["*.png","*.jpg","*.jpeg","*.gif","*.webp","*.svg","*.woff","*.woff2","*.ttf","*.css"]})
    driver.execute_cdp_cmd("Network.enable", {})

block_heavy_resources(driver)

# -------------------------------
# Logs y medición de tiempos
# -------------------------------
timing_log = {}

def log(msg, status="info", depth=0):
    icons = {"ok": "✅", "info": "🔎", "wait": "⏳", "error": "❌", "done": "🚀"}
    print(f"{'  '*depth}{icons.get(status,'ℹ️')} {msg}")

def measure_step(func, name, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    timing_log[name] = end - start
    log(f"Tiempo de '{name}': {end - start:.2f}s", "info")
    return result

# -------------------------------
# Búsqueda rápida del botón
# -------------------------------
MAX_DEPTH = 5
IFRAME_TIMEOUT = 1

def find_and_click_start_lab_fast(driver, depth=0):
    if depth > MAX_DEPTH:
        return False

    try:
        # Intento directo
        button = WebDriverWait(driver, IFRAME_TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "launchclabsbtn"))
        )
        button.click()
        log(f"Botón Start Lab clickeado en nivel {depth}", "ok", depth)
        return True
    except:
        pass

    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for idx, iframe in enumerate(iframes):
        driver.switch_to.frame(iframe)
        found = find_and_click_start_lab_fast(driver, depth+1)
        driver.switch_to.parent_frame()
        if found:
            return True
    return False

# -------------------------------
# Script principal
# -------------------------------
try:
    wait = WebDriverWait(driver, 15)

    log("Abriendo página de login...", "wait")
    measure_step(driver.get, "LoginPage GET", "https://awsacademy.instructure.com/login/canvas")

    log("Ingresando credenciales...", "wait")
    measure_step(lambda: wait.until(EC.presence_of_element_located((By.ID, "pseudonym_session_unique_id"))).send_keys(EMAIL), "Ingresar email")
    measure_step(lambda: driver.find_element(By.ID, "pseudonym_session_password").send_keys(PASSWORD), "Ingresar password")
    measure_step(lambda: driver.find_element(By.CLASS_NAME, "Button--login").click(), "Click login")
    log("Login exitoso", "ok")

    log("Entrando al laboratorio...", "wait")
    measure_step(driver.get, "LabPage GET", LAB_URL)
    measure_step(lambda: wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe"))), "Esperar iframe principal")
    log("Página del lab cargada", "ok")

    if not measure_step(find_and_click_start_lab_fast, "FindAndClick Start Lab", driver):
        raise Exception("No se encontró el botón Start Lab")

    log("Esperando redirección a la consola AWS...", "wait")
    measure_step(lambda: wait.until(lambda d: "console.aws.amazon.com" in d.current_url or "awsacademy.instructure.com" in d.current_url), "Esperar redirección AWS")

    aws_console_url = driver.current_url
    log(f"Consola AWS lista en: {aws_console_url}", "done")

    # -------------------------------
    # Informe de tiempos
    # -------------------------------
    log("\n📊 Informe de tiempos por paso:", "done")
    for step, t in timing_log.items():
        log(f"{step}: {t:.2f}s", "info")

except Exception as e:
    log(f"Error: {e}", "error")

finally:
    driver.quit()
