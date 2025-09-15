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
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-logging")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Bloquear imágenes, CSS y fuentes pesadas
def block_heavy_resources(driver: WebDriver):
    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": [
        "*.png","*.jpg","*.jpeg","*.gif","*.webp","*.svg",
        "*.woff","*.woff2","*.ttf","*.css"
    ]})
    driver.execute_cdp_cmd("Network.enable", {})

block_heavy_resources(driver)

# -------------------------------
# Logs y medición de tiempos
# -------------------------------
timing_log = {}

def log(msg, status="info"):
    icons = {"ok": "✅", "info": "🔎", "wait": "⏳", "error": "❌", "done": "🚀"}
    print(f"{icons.get(status,'ℹ️')} {msg}")

def measure_step(func, name, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    timing_log[name] = end - start
    log(f"Tiempo de '{name}': {end - start:.2f}s", "info")
    return result

# -------------------------------
# Click Start Lab con JS puro
# -------------------------------
def click_start_lab_js(driver: WebDriver):
    script = """
    function clickInFrames(frames){
        for (let i=0;i<frames.length;i++){
            let frame = frames[i];
            try{
                let btn = frame.contentDocument.getElementById('launchclabsbtn');
                if(btn){ btn.click(); return true; }
                let found = clickInFrames(frame.contentDocument.getElementsByTagName('iframe'));
                if(found) return true;
            }catch(e){}
        }
        return false;
    }
    let btn = document.getElementById('launchclabsbtn');
    if(btn){ btn.click(); true; } else { clickInFrames(document.getElementsByTagName('iframe')); }
    """
    driver.execute_script(script)

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

    log("Click Start Lab usando JS puro...", "wait")
    measure_step(click_start_lab_js, "FindAndClick Start Lab", driver)
    log("Botón Start Lab clickeado", "ok")

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
