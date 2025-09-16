#!/usr/bin/env bash
set -e

# Ir a la carpeta del script
cd "$(dirname "$0")"

# -------------------------------
# Preparar entorno virtual
# -------------------------------
if [ ! -d "env" ]; then
  echo "🔧 Creando entorno virtual..."
  python3 -m venv env
fi

# Activar entorno virtual
source env/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --quiet -r requirements.txt

# -------------------------------
# Ejecutar script de Python
# -------------------------------
echo "🚀 Ejecutando LogAWStudent..."
python main.py
