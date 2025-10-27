# src/logawstudent/cli.py
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from .utils import set_env, unset_env, load_env, clear_env, update_env, get_credentials_status, get_env_file
from .core import launch_lab

console = Console()

app = typer.Typer(
    help="CLI para automatizar login y labs de AWS Academy",
    no_args_is_help=False,
    add_completion=False
)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """LogAWStudent - CLI para automatizar login y labs de AWS Academy"""
    if ctx.invoked_subcommand is None:
        show_main_info()

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

def show_main_info():
    """Muestra información principal del proyecto cuando se ejecuta solo 'awstudent'."""
    # Información del proyecto
    console.print(Panel(
        "🚀 CLI para automatizar login y labs de AWS Academy\n\n"
        "Este proyecto automatiza el inicio de sesión en AWS Academy y el lanzamiento\n"
        "de un laboratorio a través de Selenium y Python. Es útil para estudiantes de\n"
        "AWS Academy que necesitan realizar este proceso repetidamente.\n\n"
        "📦 Características:\n"
        "• Login automático en AWS Academy\n"
        "• Lanzamiento automático de laboratorios\n"
        "• Gestión de credenciales segura\n"
        "• Interfaz CLI intuitiva\n"
        "• Modo headless para mayor eficiencia",
        title="🎯 LogAWStudent",
        border_style="blue"
    ))
    
    # Información del autor
    console.print(Panel(
        "👨‍💻 Autor: Lazheart\n"
        "🔗 Repositorio: https://github.com/Lazheart/LogAWStudent\n"
        "⭐ Estrellas: 4\n"
        "🍴 Forks: 0\n"
        "📝 Licencia: Open Source",
        title="👤 Información del Proyecto",
        border_style="green"
    ))
    
    # Comandos disponibles
    console.print(Panel(
        "📋 Comandos disponibles:\n\n"
        "• awstudent login     - Gestiona credenciales de login\n"
        "• awstudent url       - Configura URL del laboratorio\n"
        "• awstudent start     - Inicia el laboratorio automáticamente\n"
        "• awstudent status    - Muestra estado de credenciales\n"
        "• awstudent clean     - Limpia credenciales específicas\n\n"
        "🧹 Opciones de limpieza:\n"
        "• awstudent login --clean email    - Elimina solo el email\n"
        "• awstudent login --clean password - Elimina solo la contraseña\n"
        "• awstudent login --clean all      - Elimina email y contraseña\n"
        "• awstudent url --clean            - Elimina la URL del laboratorio\n\n"
        "💡 Usa 'awstudent <comando> --help' para más información",
        title="📚 Comandos Disponibles",
        border_style="yellow"
    ))
    
    # Estado actual
    show_credentials_status()

@app.command()
def login(
    status: bool = typer.Option(False, "--status", help="Muestra el estado de las credenciales"),
    update: bool = typer.Option(False, "--update", help="Actualiza credenciales existentes"),
    force: bool = typer.Option(False, "--force", help="Fuerza la sobrescritura sin preguntar"),
    delete: bool = typer.Option(False, "--delete", help="Elimina las credenciales de login"),
    clean: str = typer.Option(None, "--clean", help="Limpia credenciales específicas: 'email', 'password', o 'all'")
):
    """Guarda o actualiza credenciales (email y password) en .env"""
    if status:
        show_credentials_status()
        return
    
    if clean:
        if clean == "email":
            unset_env("EMAIL")
            console.print(Panel("🧹 Email eliminado.", 
                               title="🧹 Limpieza", border_style="yellow"))
        elif clean == "password":
            unset_env("PASSWORD")
            console.print(Panel("🧹 Password eliminada.", 
                               title="🧹 Limpieza", border_style="yellow"))
        elif clean == "all":
            unset_env("EMAIL")
            unset_env("PASSWORD")
            console.print(Panel("🧹 Todas las credenciales de login eliminadas.", 
                               title="🧹 Limpieza Completa", border_style="yellow"))
        else:
            console.print(Panel("❌ Opción inválida para --clean. Usa: 'email', 'password', o 'all'", 
                               title="❌ Error", border_style="red"))
        return
    
    if delete:
        unset_env("EMAIL")
        unset_env("PASSWORD")
        console.print(Panel("🧹 Credenciales de login eliminadas.", 
                           title="🧹 Eliminado", border_style="yellow"))
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
    unset: bool = typer.Option(False, "--unset", help="[DEPRECATED] Usa --delete en su lugar"),
    update: bool = typer.Option(False, "--update", help="Actualiza la URL del laboratorio"),
    delete: bool = typer.Option(False, "--delete", help="Elimina la URL del laboratorio"),
    clean: bool = typer.Option(False, "--clean", help="Limpia la URL del laboratorio")
):
    """Configura, actualiza o elimina la URL del laboratorio."""
    if clean:
        unset_env("LAB_URL")
        console.print(Panel("🧹 URL del laboratorio eliminada.", 
                           title="🧹 Limpieza", border_style="yellow"))
        return
    
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
    elif unset or delete:
        if unset:
            console.print(Panel("⚠️  --unset está deprecado. Usa --delete en su lugar.", 
                               title="⚠️  Deprecado", border_style="yellow"))
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
def start(
    force: bool = typer.Option(False, "--force", help="Fuerza el inicio sin verificar credenciales"),
    status: bool = typer.Option(False, "--status", help="Muestra el estado antes de iniciar")
):
    """Inicia el laboratorio automáticamente."""
    if status:
        show_credentials_status()
        return
    
    # Verificar credenciales antes de iniciar
    try:
        from .utils import validate_credentials
        validate_credentials()
        console.print(Panel("🚀 Iniciando laboratorio...", 
                           title="🚀 Iniciando", border_style="blue"))
        launch_lab()
    except ValueError as e:
        if force:
            console.print(Panel("⚠️  Iniciando sin credenciales completas...", 
                               title="⚠️  Modo Forzado", border_style="yellow"))
            launch_lab()
        else:
            console.print(Panel(f"❌ {e}\n💡 Usa 'awstudent login --status' para ver qué credenciales faltan", 
                               title="❌ Error", border_style="red"))

@app.command()
def status(
    verbose: bool = typer.Option(False, "--verbose", help="Muestra información detallada"),
    force: bool = typer.Option(False, "--force", help="Fuerza la actualización del estado")
):
    """Muestra el estado de todas las credenciales."""
    if verbose:
        # Mostrar información adicional
        env_file = get_env_file()
        console.print(Panel(f"📁 Archivo de configuración: {env_file}", 
                           title="📁 Información del Sistema", border_style="blue"))
    
    show_credentials_status()

@app.command()
def clean(
    all: bool = typer.Option(False, "--all", help="Elimina todas las credenciales"),
    login: bool = typer.Option(False, "--login", help="Elimina solo las credenciales de login"),
    url: bool = typer.Option(False, "--url", help="Elimina solo la URL del laboratorio"),
    force: bool = typer.Option(False, "--force", help="Fuerza la limpieza sin confirmar")
):
    """Limpia credenciales específicas o todas las credenciales."""
    if all:
        if not force:
            confirm = typer.confirm("¿Estás seguro de que quieres eliminar TODAS las credenciales?")
            if not confirm:
                console.print("Operación cancelada.", style="yellow")
                return
        clear_env()
        console.print(Panel("🧹 Todas las credenciales han sido eliminadas.", 
                           title="🧹 Limpieza Completa", border_style="yellow"))
    elif login:
        unset_env("EMAIL")
        unset_env("PASSWORD")
        console.print(Panel("🧹 Credenciales de login eliminadas.", 
                           title="🧹 Limpieza de Login", border_style="yellow"))
    elif url:
        unset_env("LAB_URL")
        console.print(Panel("🧹 URL del laboratorio eliminada.", 
                           title="🧹 Limpieza de URL", border_style="yellow"))
    else:
        # Mostrar ayuda si no se especifica qué limpiar
        console.print(Panel("💡 Especifica qué quieres limpiar:\n"
                           "• awstudent clean --all: Elimina todas las credenciales\n"
                           "• awstudent clean --login: Elimina solo credenciales de login\n"
                           "• awstudent clean --url: Elimina solo la URL del laboratorio", 
                           title="🧹 Comando Clean", border_style="blue"))

if __name__ == "__main__":
    app()
