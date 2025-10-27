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
    # options.add_argument("--headless=new")
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
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ic-Layout-wrapper")))
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
            
            # Verificar si hay error 400 o similar en la URL o contenido
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            
            # Detectar errores comunes de autenticación
            if ("error" in current_url or 
                "400" in page_source or 
                "unauthorized" in page_source or
                "invalid" in page_source or
                "incorrect" in page_source):
                log("Error de autenticación detectado. Credenciales incorrectas.", "error")
                return False
            
            # Si llegamos aquí, asumir que el login fue exitoso pero no se pudo verificar
            log("No se pudo verificar el login completamente, pero continuando...", "info")
            return True

    except Exception as e:
        log(f"Error durante el login: {e}", "error")
        return False


def detect_auth_error(driver: WebDriver) -> bool:
    """
    Detecta si hay errores de autenticación en la página actual.
    
    Args:
        driver: WebDriver en la página actual
        
    Returns:
        bool: True si hay error de autenticación, False en caso contrario
    """
    try:
        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()
        
        # Detectar errores específicos de autenticación
        auth_errors = [
            "error", "400", "401", "403", "unauthorized", "forbidden",
            "invalid", "incorrect", "wrong", "failed", "denied",
            "login failed", "authentication failed", "access denied"
        ]
        
        # Verificar en URL y contenido de la página
        for error in auth_errors:
            if error in current_url or error in page_source:
                return True
        
        # Verificar elementos específicos de error
        try:
            error_selectors = [
                ".error_message", ".alert-error", ".error", 
                ".login-error", ".auth-error", ".invalid-credentials"
            ]
            
            for selector in error_selectors:
                try:
                    error_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if error_element.is_displayed():
                        return True
                except:
                    continue
        except:
            pass
        
        return False
        
    except Exception:
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
    
    # Verificación adicional de errores de autenticación
    if success and detect_auth_error(driver):
        log("Error de autenticación detectado después del login", "error")
        success = False
    
    return driver, success
