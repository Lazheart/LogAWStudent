#!/usr/bin/env bash

# -------------------------------
# Variables de entorno (opcional)
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

# Ejecutar script de Python
python3 main.py
