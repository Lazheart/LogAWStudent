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
