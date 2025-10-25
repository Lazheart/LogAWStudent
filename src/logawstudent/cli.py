# src/logawstudent/cli.py
import typer
from .utils import set_env, unset_env, load_env, clear_env
from .core import launch_lab

app = typer.Typer(help="CLI para automatizar login y labs de AWS Academy")

@app.command()
def login():
    """Guarda credenciales (email y password) en .env"""
    email = typer.prompt("Ingrese su EMAIL")
    password = typer.prompt("Ingrese su PASSWORD", hide_input=True)
    set_env("EMAIL", email)
    set_env("PASSWORD", password)
    typer.echo("✅ Credenciales guardadas exitosamente.")

@app.command()
def url(
    set: bool = typer.Option(False, "--set", help="Establece la URL del laboratorio"),
    unset: bool = typer.Option(False, "--unset", help="Elimina la URL del laboratorio")
):
    """Configura o elimina la URL del laboratorio."""
    if set:
        lab_url = typer.prompt("Ingrese la URL del LAB")
        set_env("LAB_URL", lab_url)
        typer.echo("✅ URL del laboratorio guardada.")
    elif unset:
        unset_env("LAB_URL")
        typer.echo("🧹 URL del laboratorio eliminada.")
    else:
        data = load_env()
        typer.echo(f"🔗 URL actual: {data.get('LAB_URL', 'No configurada')}")

@app.command()
def logout():
    """Elimina todas las credenciales almacenadas."""
    clear_env()
    typer.echo("👋 Credenciales eliminadas exitosamente.")

@app.command()
def start():
    """Inicia el laboratorio automáticamente."""
    typer.echo("🚀 Iniciando laboratorio...")
    launch_lab()

if __name__ == "__main__":
    app()
