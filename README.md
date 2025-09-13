# LogAWStudent

Este proyecto automatiza el inicio de sesión en AWS Academy y el lanzamiento de un laboratorio a través de Selenium y Python. Es útil para estudiantes de AWS Academy que necesitan realizar este proceso repetidamente, ahorrando tiempo y esfuerzo.

## Descripción

`LogAWStudent` es un script de automatización desarrollado en Python que realiza las siguientes tareas:

1. Inicia sesión en el portal de AWS Academy utilizando las credenciales del usuario.
2. Accede a la URL del laboratorio proporcionada.
3. Hace clic en el botón para iniciar el laboratorio.
4. Obtiene la URL de la consola de AWS después de redirigir a la página correspondiente.

## Requisitos

Este proyecto utiliza Selenium para la automatización del navegador, junto con `python-dotenv` para manejar variables de entorno (como las credenciales de inicio de sesión) y `webdriver-manager` para gestionar automáticamente el controlador de Chrome.

Para instalar los requisitos, ejecuta:

```bash
pip install -r requirements.txt
```

## Configuración

1. **Variables de Entorno**:
   Crea un archivo `.env` en el directorio raíz del proyecto y agrega las siguientes variables:

   ```
   EMAIL=tu_correo@example.com
   PASSWORD=tu_contraseña
   LAB_URL=https://url_del_laboratorio
   ```

   Asegúrate de reemplazar `tu_correo@example.com`, `tu_contraseña` y `https://url_del_laboratorio` con tus datos reales.

2. **Instalar Dependencias**:
   Asegúrate de tener todas las dependencias necesarias instaladas ejecutando:

   ```bash
   pip install -r requirements.txt
   ```

## Uso

Para ejecutar el script, simplemente corre el archivo `main.py`:

```bash
python main.py
```

El script abrirá el navegador de manera *headless* (sin interfaz gráfica), realizará el inicio de sesión en AWS Academy, y lanzará el laboratorio.

**Nota**: Si deseas ver el navegador mientras el script se ejecuta, puedes eliminar o comentar la línea:

```python
options.add_argument("--headless=new")
```

## Contribución

Si tienes alguna sugerencia o mejora, no dudes en abrir un "issue" o hacer un "pull request".


