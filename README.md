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
- [webdriver-manager](https://pypi.org/project/webdriver-manager/) → Descarga automática del controlador  
- [python-dotenv](https://pypi.org/project/python-dotenv/) → Manejo de variables de entorno  

Necesitas tener instalado **Python 3.8+** y **Google Chrome**.

---

## ⚙️ Instalación y uso

### 🔹 Paso 1: Clonar el repositorio

```bash
git clone https://github.com/usuario/lazheart-logawstudent.git
cd lazheart-logawstudent
````

### 🔹 Paso 2: Configurar las variables de entorno (opcional)

Si quieres evitar ingresar credenciales manualmente cada vez:

1. Copia el archivo de ejemplo:

   ```bash
   cp .env_example .env
   ```

2. Edita `.env` con tus credenciales reales:

   ```env
   EMAIL=tu_correo@example.com
   PASSWORD=tu_contraseña
   LAB_URL=https://awsacademy.instructure.com/courses/.../modules/items/...
   ```

---

### 🔹 Paso 3: Ejecutar el script

El script `loginUpAWS.sh` se encarga de todo:

* Crear un entorno virtual (si no existe).
* Instalar dependencias (`requirements.txt`).
* Pedir credenciales (si no hay `.env`).
* Ejecutar el bot de Selenium.

Ejecuta:

```bash
chmod +x loginUpAWS.sh   # (solo la primera vez)
./loginUpAWS.sh
```

---

## ▶️ Notas

* Por defecto, el navegador se abre en **modo headless** (sin interfaz).
* Si deseas ver el navegador durante la ejecución, comenta esta línea en `main.py`:

```python
options.add_argument("--headless=new")
```

---

## 🤝 Contribución

Si tienes sugerencias o mejoras, abre un *issue* o envía un *pull request*.
