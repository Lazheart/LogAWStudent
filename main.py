import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------
# Cargar variables del entorno
# -------------------------------
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
LAB_URL = os.getenv("LAB_URL")

# -------------------------------
# Configurar Selenium (headless para que no abra ventana)
# -------------------------------
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")   # quita esta línea si quieres ver el navegador
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# WebDriver con webdriver-manager (se baja el driver correcto)
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), 
    options=options
)

try:
    # 1. Ir al login de AWS Academy
    driver.get("https://awsacademy.instructure.com/login/canvas")
    time.sleep(3)

    # 2. Completar login
    driver.find_element(By.ID, "pseudonym_session_unique_id").send_keys(EMAIL)
    driver.find_element(By.ID, "pseudonym_session_password").send_keys(PASSWORD)
    driver.find_element(By.CLASS_NAME, "Button--login").click()
    time.sleep(5)

    # 3. Ir al laboratorio
    driver.get(LAB_URL)
    time.sleep(5)

    # 4. Dar click en "Start Lab"
    start_lab = driver.find_element(By.ID, "launchclabsbtn")
    start_lab.click()
    time.sleep(10)  # esperar redirección a la consola AWS

    # 5. Guardar la URL actual (consola AWS)
    aws_console_url = driver.current_url
    print("✅ Consola AWS lista en:", aws_console_url)

except Exception as e:
    print("❌ Error:", e)

finally:
    driver.quit()
