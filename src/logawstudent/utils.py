# src/logawstudent/utils.py
import os
from dotenv import load_dotenv

ENV_FILE = ".env"

def load_env():
    load_dotenv()
    return {
        "EMAIL": os.getenv("EMAIL"),
        "PASSWORD": os.getenv("PASSWORD"),
        "LAB_URL": os.getenv("LAB_URL"),
    }

def set_env(key, value):
    env_data = load_env()
    env_data[key] = value
    with open(ENV_FILE, "w") as f:
        for k, v in env_data.items():
            if v:
                f.write(f"{k}={v}\n")

def update_env(key, value):
    """Actualiza una credencial existente."""
    env_data = load_env()
    if key not in env_data or not env_data[key]:
        raise ValueError(f"La credencial {key} no existe. Usa 'awstudent login' primero.")
    env_data[key] = value
    with open(ENV_FILE, "w") as f:
        for k, v in env_data.items():
            if v:
                f.write(f"{k}={v}\n")

def unset_env(key):
    env_data = load_env()
    if key in env_data:
        env_data[key] = None
    with open(ENV_FILE, "w") as f:
        for k, v in env_data.items():
            if v:
                f.write(f"{k}={v}\n")

def clear_env():
    if os.path.exists(ENV_FILE):
        os.remove(ENV_FILE)

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
