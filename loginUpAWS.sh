#!/usr/bin/env bash

set -e  # detener si hay error

# -------------------------------
# Preparar entorno virtual
# -------------------------------
if [ ! -d "env" ]; then
  echo "🔧 Creando entorno virtual..."
  python3 -m venv env
fi

# Activar entorno virtual
source env/bin/activate

# Instalar dependencias si no están
echo "📦 Instalando dependencias..."
pip install --quiet -r requirements.txt

# -------------------------------
# Variables de entorno
# -------------------------------
EMAIL="${EMAIL:-}"
PASSWORD="${PASSWORD:-}"
LAB_URL="${LAB_URL:-}"

# Pedir datos si no existen
if [ -z "$EMAIL" ]; then
  read -p "Ingrese su EMAIL: " EMAIL
fi

if [ -z "$PASSWORD" ]; then
  read -s -p "Ingrese su PASSWORD: " PASSWORD
  echo
fi

if [ -z "$LAB_URL" ]; then
  read -p "Ingrese la URL del LAB: " LAB_URL
fi

# -------------------------------
# Ejecutar script de Python
# -------------------------------
echo "🚀 Ejecutando LogAWStudent..."
python main.py
