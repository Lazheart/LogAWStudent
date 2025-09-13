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
options.add_argument("--headless=new")   # comenta para ver en el navegador
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), 
    options=options
)

# -------------------------------
# Función para logs bonitos
# -------------------------------
def log(msg, status="info"):
    icons = {"ok": "✅", "info": "🔎", "wait": "⏳", "error": "❌", "done": "🚀"}
    print(f"{icons.get(status,'ℹ️')} {msg}")

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

    # 3. Intentar encontrar el botón en DOM principal
    
    try:
        start_lab = wait.until(EC.presence_of_element_located((By.ID, "launchclabsbtn")))
        driver.execute_script("arguments[0].click();", start_lab)
        log("Botón Start Lab encontrado en DOM principal", "ok")
    except:
        log("Botón no visible en DOM principal, buscando en iframes...", "info")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        log(f"Encontrados {len(iframes)} iframes", "info")

        clicked = False
        for idx, iframe in enumerate(iframes):
            driver.switch_to.default_content()
            driver.switch_to.frame(iframe)
            try:
                start_lab = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "launchclabsbtn"))
                )
                driver.execute_script("arguments[0].click();", start_lab)
                log(f"Start Lab encontrado en iframe {idx}", "ok")
                clicked = True
                break
            except:
                continue
        driver.switch_to.default_content()
        if not clicked:
            raise Exception("No se encontró el botón Start Lab en ningún iframe")

    # 4. Esperar redirección a la consola AWS
    log("Esperando redirección a la consola AWS...", "wait")
    wait.until(lambda d: "console.aws.amazon.com" in d.current_url or "awsacademy.instructure.com" in d.current_url)

    aws_console_url = driver.current_url
    log(f"Consola AWS lista en: {aws_console_url}", "done")

except Exception as e:
    log(f"Error: {e}", "error")

finally:
    driver.quit()
