# src/logawstudent/lab.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
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


def check_lab_status(driver: WebDriver, timeout=10):
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


def click_start_lab_fast(driver: WebDriver, timeout=10):
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


def navigate_to_lab(driver: WebDriver) -> bool:
    """
    Navega a la página del laboratorio.
    
    Args:
        driver: WebDriver autenticado
        
    Returns:
        bool: True si la navegación fue exitosa
    """
    try:
        creds = validate_credentials()
        lab_url = creds["LAB_URL"]
    except ValueError as e:
        log(f"Error de credenciales: {e}", "error")
        return False

    try:
        log("Entrando al laboratorio...", "wait")
        driver.get(lab_url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        log("Página del lab cargada", "ok")
        return True
    except Exception as e:
        log(f"Error navegando al laboratorio: {e}", "error")
        return False


def wait_for_lab_ready(driver: WebDriver, max_wait=50):
    """
    Espera a que el laboratorio esté listo.
    
    Args:
        driver: WebDriver en la página del lab
        max_wait: Tiempo máximo de espera en segundos
        
    Returns:
        bool: True si el lab está listo, False si no se pudo iniciar
    """
    start_wait = time.time()
    while time.time() - start_wait < max_wait:
        status = check_lab_status(driver, timeout=10)
        if status and "Ready" in status:
            log("Laboratorio ya está iniciado y listo", "ok")
            return True
        log("⏳ Esperando que el laboratorio se inicie...", "wait")
        time.sleep(2)
    
    log("El laboratorio no se inició en el tiempo esperado", "error")
    return False


def handle_lab_initialization(driver: WebDriver):
    """
    Maneja el proceso de inicialización del laboratorio.
    
    Args:
        driver: WebDriver en la página del lab
        
    Returns:
        bool: True si el lab está listo, False en caso contrario
    """
    log("Laboratorio se está iniciando, esperando a que esté listo...", "wait")
    max_wait = 35
    start_wait = time.time()
    
    while time.time() - start_wait < max_wait:
        status = check_lab_status(driver, timeout=10)
        if status and "Ready" in status:
            log("Laboratorio ya está iniciado y listo", "ok")
            return True
        log("Sigue iniciando...", "wait")
        time.sleep(2)
    
    log("El laboratorio no pasó a 'Ready' en el tiempo esperado", "error")
    return False


def start_terminated_lab(driver: WebDriver):
    """
    Inicia un laboratorio que está terminado.
    
    Args:
        driver: WebDriver en la página del lab
        
    Returns:
        bool: True si el lab se inició correctamente, False en caso contrario
    """
    log("Laboratorio detenido, intentando iniciarlo...", "wait")
    
    if click_start_lab_fast(driver, timeout=15):
        log("🚀 Botón Start Lab clickeado", "ok")
        return wait_for_lab_ready(driver, max_wait=200)
    else:
        log("No se pudo iniciar el laboratorio", "error")
        return False


def manage_lab_status(driver: WebDriver):
    """
    Gestiona el estado del laboratorio y lo inicia si es necesario.
    
    Args:
        driver: WebDriver en la página del lab
        
    Returns:
        bool: True si el lab está listo, False en caso contrario
    """
    log("Verificando estado del laboratorio...", "wait")
    status = check_lab_status(driver, timeout=15)

    if not status:
        log("No se pudo detectar el estado del laboratorio", "error")
        return False
    elif "Ready" in status:
        log("Laboratorio ya está iniciado y listo", "ok")
        return True
    elif "Initializing" in status:
        return handle_lab_initialization(driver)
    elif "Terminated" in status:
        return start_terminated_lab(driver)
    else:
        log(f"Estado desconocido detectado: {status}", "info")
        return False


def process_lab(driver: WebDriver) -> bool:
    """
    Procesa completamente el laboratorio: navega, verifica estado y lo inicia si es necesario.
    
    Args:
        driver: WebDriver autenticado
        
    Returns:
        bool: True si el lab está listo, False en caso contrario
    """
    # Navegar al laboratorio
    if not navigate_to_lab(driver):
        return False
    
    # Gestionar el estado del laboratorio
    return manage_lab_status(driver)
