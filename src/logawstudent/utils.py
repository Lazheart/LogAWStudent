# src/logawstudent/utils.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Rutas para archivos .env
LOCAL_ENV = Path(".env")
GLOBAL_ENV = Path.home() / ".config" / "logawstudent" / ".env"

def get_env_file():
    """Retorna la ruta del archivo .env a usar (local tiene prioridad sobre global)."""
    if LOCAL_ENV.exists():
        return LOCAL_ENV
    return GLOBAL_ENV

def ensure_global_config_dir():
    """Asegura que el directorio de configuración global existe."""
    global_dir = GLOBAL_ENV.parent
    global_dir.mkdir(parents=True, exist_ok=True)

def load_env():
    """Carga las variables de entorno desde el archivo .env apropiado."""
    env_file = get_env_file()
    load_dotenv(env_file)
    return {
        "EMAIL": os.getenv("EMAIL"),
        "PASSWORD": os.getenv("PASSWORD"),
        "LAB_URL": os.getenv("LAB_URL"),
    }

def set_env(key, value):
    """Establece una variable de entorno en el archivo .env apropiado."""
    env_data = load_env()
    env_data[key] = value
    env_file = get_env_file()
    
    # Si no existe archivo local, usar el global
    if not LOCAL_ENV.exists():
        ensure_global_config_dir()
        env_file = GLOBAL_ENV
    
    with open(env_file, "w") as f:
        for k, v in env_data.items():
            if v:
                f.write(f"{k}={v}\n")

def update_env(key, value):
    """Actualiza una credencial existente."""
    env_data = load_env()
    if key not in env_data or not env_data[key]:
        raise ValueError(f"La credencial {key} no existe. Usa 'awstudent login' primero.")
    env_data[key] = value
    env_file = get_env_file()
    
    # Si no existe archivo local, usar el global
    if not LOCAL_ENV.exists():
        ensure_global_config_dir()
        env_file = GLOBAL_ENV
    
    with open(env_file, "w") as f:
        for k, v in env_data.items():
            if v:
                f.write(f"{k}={v}\n")

def unset_env(key):
    """Elimina una variable de entorno del archivo .env."""
    env_data = load_env()
    if key in env_data:
        env_data[key] = None
    env_file = get_env_file()
    
    # Si no existe archivo local, usar el global
    if not LOCAL_ENV.exists():
        ensure_global_config_dir()
        env_file = GLOBAL_ENV
    
    with open(env_file, "w") as f:
        for k, v in env_data.items():
            if v:
                f.write(f"{k}={v}\n")

def clear_env():
    """Elimina todos los archivos .env (local y global)."""
    if LOCAL_ENV.exists():
        LOCAL_ENV.unlink()
    if GLOBAL_ENV.exists():
        GLOBAL_ENV.unlink()

def validate_credentials():
    """Valida que todas las credenciales estén presentes."""
    creds = load_env()
    missing = [k for k, v in creds.items() if not v]
    if missing:
        raise ValueError(f"Faltan credenciales: {', '.join(missing)}")
    return creds

def get_credentials_status():
    """Retorna el estado de las credenciales."""
    creds = load_env()
    status = {}
    for key, value in creds.items():
        status[key] = {
            'exists': bool(value),
            'value': value if value else None
        }
    return status
