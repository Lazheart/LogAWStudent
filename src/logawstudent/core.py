# src/logawstudent/core.py
import concurrent.futures
from .auth import authenticate_user, log
from .lab import process_lab

def launch_lab():
    """
    Lanza el laboratorio automáticamente usando módulos separados.
    Requiere que EMAIL, PASSWORD y LAB_URL estén configurados en .env.
    """
    driver = None
    
    try:
        # Autenticar usuario
        driver, auth_success = authenticate_user()
        if not auth_success or not driver:
            log("No se pudo autenticar. Deteniendo ejecución.", "error")
            return
        
        # Solo continuar si la autenticación fue exitosa
        log("✅ Autenticación exitosa. Procediendo con el laboratorio...", "ok")
        
        # Procesar laboratorio
        lab_success = process_lab(driver)
        
        if lab_success:
            log("🎉 Laboratorio iniciado exitosamente", "done")
        else:
            log("Error: No se pudo iniciar el laboratorio", "error")

    except Exception as e:
        log(f"Error inesperado: {e}", "error")

    finally:
        if driver:
            driver.quit()
