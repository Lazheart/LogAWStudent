# src/logawstudent/cli.py
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from .utils import set_env, unset_env, load_env, clear_env, update_env, get_credentials_status
from .core import launch_lab

console = Console()

app = typer.Typer(
    help="CLI para automatizar login y labs de AWS Academy",
    no_args_is_help=True,
    add_completion=False
)

def show_credentials_status():
    """Muestra el estado de las credenciales con formato elegante."""
    status = get_credentials_status()
    
    # Crear tabla para mostrar el estado
    table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
    table.add_column("Credencial", style="cyan", width=12)
    table.add_column("Estado", justify="center", width=8)
    table.add_column("Valor", style="dim", width=30)
    
    for key, info in status.items():
        if info['exists']:
            # Mostrar solo los primeros y últimos caracteres para seguridad
            value = info['value']
            if key == "PASSWORD":
                display_value = "*" * len(value) if value else "No configurado"
            elif key == "LAB_URL":
                # Para URLs, mostrar más caracteres para que sea útil
                if len(value) > 20:
                    display_value = value[:10] + "..." + value[-10:]
                else:
                    display_value = value
            else:
                display_value = value[:3] + "..." + value[-3:] if len(value) > 6 else value
            table.add_row(key, "✅", display_value)
        else:
            table.add_row(key, "❌", "No configurado")
    
    # Crear panel con la tabla
    panel_content = table
    console.print(Panel(panel_content, title="📊 Estado de las Credenciales", border_style="blue"))
    
    # Mostrar mensaje de estado
    all_configured = all(info['exists'] for info in status.values())
    if all_configured:
        console.print(Panel("🚀 Todas las credenciales están configuradas. Puedes usar 'awstudent start'", 
                           title="✅ Listo", border_style="green"))
    else:
        missing = [k for k, v in status.items() if not v['exists']]
        console.print(Panel(f"⚠️  Faltan credenciales: {', '.join(missing)}\n"
                           f"Usa 'awstudent login' y 'awstudent url --set' para configurar", 
                           title="⚠️  Configuración Incompleta", border_style="yellow"))

@app.command()
def login(
    status: bool = typer.Option(False, "--status", help="Muestra el estado de las credenciales"),
    update: bool = typer.Option(False, "--update", help="Actualiza credenciales existentes"),
    force: bool = typer.Option(False, "--force", help="Fuerza la sobrescritura sin preguntar")
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
            console.print(Panel("✅ Credenciales actualizadas exitosamente.", 
                               title="✅ Éxito", border_style="green"))
        except ValueError as e:
            console.print(Panel(f"❌ {e}", title="❌ Error", border_style="red"))
    else:
        # Verificar si ya existen credenciales
        existing_creds = load_env()
        has_existing = any(existing_creds.get(key) for key in ["EMAIL", "PASSWORD"])
        
        if has_existing and not force:
            console.print(Panel("⚠️  Ya existen credenciales guardadas.", 
                               title="⚠️  Credenciales Existentes", border_style="yellow"))
            overwrite = typer.confirm("¿Deseas sobrescribir las credenciales existentes?")
            if not overwrite:
                console.print("Operación cancelada.", style="yellow")
                return
        
        email = typer.prompt("Ingrese su EMAIL")
        password = typer.prompt("Ingrese su PASSWORD", hide_input=True)
        set_env("EMAIL", email)
        set_env("PASSWORD", password)
        console.print(Panel("✅ Credenciales guardadas exitosamente.", 
                           title="✅ Éxito", border_style="green"))

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
        console.print(Panel("✅ URL del laboratorio guardada.", 
                           title="✅ Éxito", border_style="green"))
    elif update:
        try:
            lab_url = typer.prompt("Ingrese la nueva URL del LAB")
            update_env("LAB_URL", lab_url)
            console.print(Panel("✅ URL del laboratorio actualizada.", 
                               title="✅ Éxito", border_style="green"))
        except ValueError as e:
            console.print(Panel(f"❌ {e}", title="❌ Error", border_style="red"))
    elif unset:
        unset_env("LAB_URL")
        console.print(Panel("🧹 URL del laboratorio eliminada.", 
                           title="🧹 Eliminado", border_style="yellow"))
    else:
        data = load_env()
        current_url = data.get('LAB_URL')
        if current_url and current_url != 'No configurada':
            # Mostrar solo parte de la URL por seguridad
            display_url = current_url[:30] + "..." if len(current_url) > 30 else current_url
            console.print(Panel(f"🔗 URL actual: {display_url}", 
                               title="🔗 URL del Laboratorio", border_style="blue"))
        else:
            console.print(Panel("🔗 URL actual: No configurada", 
                               title="🔗 URL del Laboratorio", border_style="blue"))

@app.command()
def logout():
    """Elimina todas las credenciales almacenadas."""
    clear_env()
    console.print(Panel("👋 Credenciales eliminadas exitosamente.", 
                       title="👋 Logout", border_style="yellow"))

@app.command()
def start():
    """Inicia el laboratorio automáticamente."""
    # Verificar credenciales antes de iniciar
    try:
        from .utils import validate_credentials
        validate_credentials()
        console.print(Panel("🚀 Iniciando laboratorio...", 
                           title="🚀 Iniciando", border_style="blue"))
        launch_lab()
    except ValueError as e:
        console.print(Panel(f"❌ {e}\n💡 Usa 'awstudent login --status' para ver qué credenciales faltan", 
                           title="❌ Error", border_style="red"))

@app.command()
def status():
    """Muestra el estado de todas las credenciales."""
    show_credentials_status()

if __name__ == "__main__":
    app()
