# src/logawstudent/auth.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from rich.console import Console
from rich.panel import Panel
from .utils import validate_credentials

console = Console()

def log(msg, status="info"):
    """Función de logging con iconos y formato Rich."""
    icons = {"ok": "✅", "info": "🔎", "wait": "⏳", "error": "❌", "done": "🚀"}
    colors = {"ok": "green", "info": "blue", "wait": "yellow", "error": "red", "done": "green"}
    
    icon = icons.get(status, "ℹ️")
    color = colors.get(status, "white")
    
    console.print(f"[{color}]{icon} {msg}[/{color}]")


def block_heavy_resources(driver: WebDriver):
    """Bloquea recursos pesados (imágenes, fuentes, CSS) para optimizar carga."""
    try:
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": [
            "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.svg",
            "*.woff", "*.woff2", "*.ttf", "*.css"
        ]})
        driver.execute_cdp_cmd("Network.enable", {})
    except Exception:
        pass


def setup_driver():
    """Configura y retorna un driver de Chrome optimizado."""
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
    
    block_heavy_resources(driver)
    return driver


def perform_login(driver: WebDriver, email: str, password: str) -> bool:
    """
    Realiza el proceso de login en AWS Academy.
    
    Args:
        driver: WebDriver configurado
        email: Email del usuario
        password: Contraseña del usuario
        
    Returns:
        bool: True si el login fue exitoso, False en caso contrario
    """
    try:
        wait = WebDriverWait(driver, 10)
        
        log("Abriendo página de login...", "wait")
        driver.get("https://awsacademy.instructure.com/login/canvas")

        log("Ingresando credenciales...", "wait")
        wait.until(EC.presence_of_element_located((By.ID, "pseudonym_session_unique_id"))).send_keys(email)
        driver.find_element(By.ID, "pseudonym_session_password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "Button--login").click()
        
        # Verificar si el login fue exitoso
        try:
            # Esperar a que aparezca el dashboard o algún elemento que indique login exitoso
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ic-DashboardCard")))
            log("Login exitoso", "ok")
            return True
        except:
            # Si no aparece el dashboard, verificar si hay mensaje de error
            try:
                error_element = driver.find_element(By.CLASS_NAME, "error_message")
                if error_element.is_displayed():
                    log("Credenciales incorrectas. Verifica tu email y contraseña.", "error")
                    return False
            except:
                pass
            log("No se pudo verificar el login. Continuando...", "info")
            return True  # Asumir éxito si no hay error explícito

    except Exception as e:
        log(f"Error durante el login: {e}", "error")
        return False


def authenticate_user() -> tuple[WebDriver, bool]:
    """
    Autentica al usuario y retorna el driver configurado.
    
    Returns:
        tuple: (driver, success) donde success indica si la autenticación fue exitosa
    """
    try:
        creds = validate_credentials()
        email = creds["EMAIL"]
        password = creds["PASSWORD"]
    except ValueError as e:
        log(f"Error de credenciales: {e}", "error")
        log("Usa 'awstudent login' y 'awstudent url --set' para configurar", "info")
        return None, False

    driver = setup_driver()
    success = perform_login(driver, email, password)
    
    return driver, success
