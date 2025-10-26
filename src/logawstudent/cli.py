# src/logawstudent/cli.py
import typer
from .utils import set_env, unset_env, load_env, clear_env, update_env, get_credentials_status
from .core import launch_lab

app = typer.Typer(
    help="CLI para automatizar login y labs de AWS Academy",
    no_args_is_help=True,
    add_completion=False
)

def show_credentials_status():
    """Muestra el estado de las credenciales."""
    status = get_credentials_status()
    typer.echo("📊 Estado de las credenciales:")
    typer.echo("=" * 40)
    
    for key, info in status.items():
        if info['exists']:
            # Mostrar solo los primeros y últimos caracteres para seguridad
            value = info['value']
            if key == "PASSWORD":
                display_value = "*" * len(value) if value else "No configurado"
            else:
                display_value = value[:3] + "..." + value[-3:] if len(value) > 6 else value
            typer.echo(f"✅ {key}: {display_value}")
        else:
            typer.echo(f"❌ {key}: No configurado")
    
    all_configured = all(info['exists'] for info in status.values())
    if all_configured:
        typer.echo("\n🚀 Todas las credenciales están configuradas. Puedes usar 'awstudent start'")
    else:
        missing = [k for k, v in status.items() if not v['exists']]
        typer.echo(f"\n⚠️  Faltan credenciales: {', '.join(missing)}")
        typer.echo("Usa 'awstudent login' y 'awstudent url --set' para configurar")

@app.command()
def login(
    status: bool = typer.Option(False, "--status", help="Muestra el estado de las credenciales"),
    update: bool = typer.Option(False, "--update", help="Actualiza credenciales existentes")
):
    """Guarda o actualiza credenciales (email y password) en .env"""
    if status:
        show_credentials_status()
        return
    
    if update:
        try:
            email = typer.prompt("Ingrese su nuevo EMAIL")
            password = typer.prompt("Ingrese su nueva PASSWORD", hide_input=True)
            update_env("EMAIL", email)
            update_env("PASSWORD", password)
            typer.echo("✅ Credenciales actualizadas exitosamente.")
        except ValueError as e:
            typer.echo(f"❌ {e}")
    else:
        email = typer.prompt("Ingrese su EMAIL")
        password = typer.prompt("Ingrese su PASSWORD", hide_input=True)
        set_env("EMAIL", email)
        set_env("PASSWORD", password)
        typer.echo("✅ Credenciales guardadas exitosamente.")

@app.command()
def url(
    set: bool = typer.Option(False, "--set", help="Establece la URL del laboratorio"),
    unset: bool = typer.Option(False, "--unset", help="Elimina la URL del laboratorio"),
    update: bool = typer.Option(False, "--update", help="Actualiza la URL del laboratorio")
):
    """Configura, actualiza o elimina la URL del laboratorio."""
    if set:
        lab_url = typer.prompt("Ingrese la URL del LAB")
        set_env("LAB_URL", lab_url)
        typer.echo("✅ URL del laboratorio guardada.")
    elif update:
        try:
            lab_url = typer.prompt("Ingrese la nueva URL del LAB")
            update_env("LAB_URL", lab_url)
            typer.echo("✅ URL del laboratorio actualizada.")
        except ValueError as e:
            typer.echo(f"❌ {e}")
    elif unset:
        unset_env("LAB_URL")
        typer.echo("🧹 URL del laboratorio eliminada.")
    else:
        data = load_env()
        current_url = data.get('LAB_URL')
        if current_url and current_url != 'No configurada':
            # Mostrar solo parte de la URL por seguridad
            display_url = current_url[:30] + "..." if len(current_url) > 30 else current_url
            typer.echo(f"🔗 URL actual: {display_url}")
        else:
            typer.echo(f"🔗 URL actual: No configurada")

@app.command()
def logout():
    """Elimina todas las credenciales almacenadas."""
    clear_env()
    typer.echo("👋 Credenciales eliminadas exitosamente.")

@app.command()
def start():
    """Inicia el laboratorio automáticamente."""
    # Verificar credenciales antes de iniciar
    try:
        from .utils import validate_credentials
        validate_credentials()
        typer.echo("🚀 Iniciando laboratorio...")
        launch_lab()
    except ValueError as e:
        typer.echo(f"❌ {e}")
        typer.echo("💡 Usa 'awstudent login --status' para ver qué credenciales faltan")

@app.command()
def status():
    """Muestra el estado de todas las credenciales."""
    show_credentials_status()

if __name__ == "__main__":
    app()
