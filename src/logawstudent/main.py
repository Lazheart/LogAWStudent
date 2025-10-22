import os
import time
from getpass import getpass
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


def log(msg, status="info"):
    icons = {"ok": "✅", "info": "🔎", "wait": "⏳", "error": "❌", "done": "🚀"}
    print(f"{icons.get(status,'ℹ️')} {msg}")


def block_heavy_resources(driver: WebDriver):
    """Bloquea recursos pesados (imágenes, fuentes, CSS)."""
    try:
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": [
            "*.png","*.jpg","*.jpeg","*.gif","*.webp","*.svg",
            "*.woff","*.woff2","*.ttf","*.css"
        ]})
        driver.execute_cdp_cmd("Network.enable", {})
    except Exception:
        pass


def check_lab_status(driver: WebDriver, timeout=20):
    """Consulta el estado del laboratorio leyendo #vmstatus dentro de #vmBtn si existe."""
    start = time.time()

    while time.time() - start < timeout:
        frames = driver.find_elements(By.TAG_NAME, "iframe")

        for frame in frames:
            try:
                driver.switch_to.frame(frame)

                # Caso 1: el botón de AWS existe
                try:
                    vm_btn = driver.find_element(By.ID, "vmBtn")
                    vm_status = vm_btn.find_element(By.ID, "vmstatus")
                    status_text = (
                        vm_status.get_attribute("aria-label")
                        or vm_status.get_attribute("title")
                        or vm_status.get_attribute("class")
                    )
                    driver.switch_to.default_content()
                    return status_text.strip()
                except:
                    pass

                # Caso 2: buscar vmstatus directamente
                try:
                    vm_status = driver.find_element(By.ID, "vmstatus")
                    status_text = (
                        vm_status.get_attribute("aria-label")
                        or vm_status.get_attribute("title")
                        or vm_status.get_attribute("class")
                    )
                    driver.switch_to.default_content()
                    return status_text.strip()
                except:
                    pass

            except:
                pass
            finally:
                driver.switch_to.default_content()

        time.sleep(1)

    return None


def click_start_lab_fast(driver: WebDriver, timeout=15):
    """Hace clic rápido en el botón Start Lab si está disponible."""
    start = time.time()
    while time.time() - start < timeout:
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        for frame in frames:
            try:
                driver.switch_to.frame(frame)
                btns = driver.find_elements(By.ID, "launchclabsbtn")
                if btns:
                    btn = btns[0]
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        driver.switch_to.default_content()
                        return True
            except:
                pass
            finally:
                driver.switch_to.default_content()
        time.sleep(1)
    return False


def main():
    # -------------------------------
    # Cargar variables del entorno
    # -------------------------------
    load_dotenv()

    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    LAB_URL = os.getenv("LAB_URL")

    # Si no existen, pedirlas y guardarlas en .env
    if not EMAIL or not PASSWORD or not LAB_URL:
        if not EMAIL:
            EMAIL = input("Ingrese su EMAIL: ")
        if not PASSWORD:
            PASSWORD = getpass("Ingrese su PASSWORD: ")
        if not LAB_URL:
            LAB_URL = input("Ingrese la URL del LAB: ")

        with open(".env", "w") as f:
            f.write(f"EMAIL={EMAIL}\n")
            f.write(f"PASSWORD={PASSWORD}\n")
            f.write(f"LAB_URL={LAB_URL}\n")

    # -------------------------------
    # Configurar Selenium
    # -------------------------------
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # opcional
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    block_heavy_resources(driver)

    try:
        wait = WebDriverWait(driver, 10)

        log("Abriendo página de login...", "wait")
        driver.get("https://awsacademy.instructure.com/login/canvas")

        log("Ingresando credenciales...", "wait")
        wait.until(EC.presence_of_element_located((By.ID, "pseudonym_session_unique_id"))).send_keys(EMAIL)
        driver.find_element(By.ID, "pseudonym_session_password").send_keys(PASSWORD)
        driver.find_element(By.CLASS_NAME, "Button--login").click()
        log("Login exitoso", "ok")

        log("Entrando al laboratorio...", "wait")
        driver.get(LAB_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        log("Página del lab cargada", "ok")

        log("Verificando estado del laboratorio...", "wait")
        status = check_lab_status(driver, timeout=15)

        if not status:
            log("No se pudo detectar el estado del laboratorio", "error")
        elif "Ready" in status:
            log("Laboratorio ya está iniciado y listo", "ok")
        elif "Initializing" in status:
            log(" Laboratorio se está iniciando, esperando a que esté listo...", "wait")
            # Espera extendida hasta 1 minuto
            max_wait = 60
            start_wait = time.time()
            while time.time() - start_wait < max_wait:
                status = check_lab_status(driver, timeout=10)
                if status and "Ready" in status:
                    log(" Laboratorio ya está iniciado y listo", "ok")
                    break
                log("⏳ Sigue iniciando...", "wait")
                time.sleep(5)
            else:
                log("❌ El laboratorio no pasó a 'Ready' en el tiempo esperado", "error")
        elif "Terminated" in status:
            log("⚠️ Laboratorio detenido, intentando iniciarlo...", "wait")
            if click_start_lab_fast(driver, timeout=15):
                log("🚀 Botón Start Lab clickeado", "ok")
                # Después de clic, esperar a que pase a Ready
                max_wait = 300
                start_wait = time.time()
                while time.time() - start_wait < max_wait:
                    status = check_lab_status(driver, timeout=10)
                    if status and "Ready" in status:
                        log(" Laboratorio ya está iniciado y listo", "ok")
                        break
                    log("⏳ Esperando que el laboratorio se inicie...", "wait")
                    time.sleep(5)
                else:
                    log("❌ El laboratorio no se inició en el tiempo esperado", "error")
            else:
                log("❌ No se pudo iniciar el laboratorio", "error")
        else:
            log(f"Estado desconocido detectado: {status}", "info")

    except Exception as e:
        log(f"Error: {e}", "error")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
