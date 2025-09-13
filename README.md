

# LogAWStudent

Este proyecto automatiza el inicio de sesión en **AWS Academy** y el lanzamiento de un laboratorio a través de **Selenium y Python**.  
Es útil para estudiantes de AWS Academy que necesitan realizar este proceso repetidamente, ahorrando tiempo y esfuerzo.

---

## 🚀 Descripción

`LogAWStudent` realiza las siguientes tareas:

1. Inicia sesión en el portal de AWS Academy utilizando las credenciales del usuario.
2. Accede a la URL del laboratorio definida en las variables de entorno.
3. Hace clic en el botón **Start Lab** para lanzar el laboratorio.
4. Obtiene y muestra en consola la URL de la consola de AWS.

---

## 📦 Requisitos

Este proyecto utiliza:

- [Selenium](https://pypi.org/project/selenium/) → Automatización del navegador
- [webdriver-manager](https://pypi.org/project/webdriver-manager/) → Descarga automática del controlador (Chrome/Firefox)
- [python-dotenv](https://pypi.org/project/python-dotenv/) → Manejo de variables de entorno

---

## ⚙️ Instalación

1. **Clona el repositorio**:

   ```bash
   git clone https://github.com/usuario/lazheart-logawstudent.git
   cd lazheart-logawstudent


2. **Crea un entorno virtual** (recomendado):

   ```bash
   python -m venv env
   source env/bin/activate      # Linux / Mac
   env\Scripts\activate         # Windows
   ```

3. **Instala dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🔑 Configuración

1. **Variables de entorno**

   Cambia el nombre de `.env_example` a `.env`:
   ``` terminal
   mv [nombre_antiguo] [nombre_nuevo]
   ```



3. **Editar `.env`** con tus credenciales reales.

   ```env
   EMAIL=tu_correo@example.com
   PASSWORD=tu_contraseña
   LAB_URL=https://awsacademy.instructure.com/courses/.../modules/items/...
   ```

---

## ▶️ Uso

Ejecuta el script principal:

```bash
python main.py
```

### Notas:

* Por defecto, el navegador se abre en **modo headless** (sin interfaz).
* Si deseas ver el navegador durante la ejecución, comenta la línea en `main.py`:

```python
options.add_argument("--headless=new")
```


## 🤝 Contribución

Si tienes sugerencias o mejoras, abre un *issue* o envía un *pull request*.


