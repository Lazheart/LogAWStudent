import os
import time
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
# options.add_argument("--headless=new")   # comenta para ver navegador
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), 
    options=options
)

try:
    # 1. Login
    driver.get("https://awsacademy.instructure.com/login/canvas")
    time.sleep(3)
    driver.find_element(By.ID, "pseudonym_session_unique_id").send_keys(EMAIL)
    driver.find_element(By.ID, "pseudonym_session_password").send_keys(PASSWORD)
    driver.find_element(By.CLASS_NAME, "Button--login").click()
    time.sleep(2)
    print("✅ Login correcto")

    # 2. Ir al lab
    driver.get(LAB_URL)
    time.sleep(3)
    print("✅ Página del lab cargada")

    wait = WebDriverWait(driver, 20)

    # 3. Intentar encontrar el botón en el DOM principal
    try:
        start_lab = wait.until(EC.presence_of_element_located((By.ID, "launchclabsbtn")))
        driver.execute_script("arguments[0].click();", start_lab)
        print("✅ Botón Start Lab encontrado en DOM principal")
    except:
        print("🔎 No está en el DOM principal, probando iframes...")

        # 4. Listar todos los iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Encontrados {len(iframes)} iframes")

        clicked = False
        for idx, iframe in enumerate(iframes):
            driver.switch_to.default_content()
            driver.switch_to.frame(iframe)
            try:
                start_lab = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "launchclabsbtn"))
                )
                driver.execute_script("arguments[0].click();", start_lab)
                print(f"✅ Botón Start Lab encontrado en iframe {idx}")
                clicked = True
                break
            except:
                continue

        driver.switch_to.default_content()
        if not clicked:
            raise Exception("❌ No se encontró el botón Start Lab en ningún iframe")

    # 5. Esperar la redirección a la consola AWS
    time.sleep(10)
    aws_console_url = driver.current_url
    print("🌍 Consola AWS lista en:", aws_console_url)

except Exception as e:
    print("❌ Error:", e)

finally:
    driver.quit()

