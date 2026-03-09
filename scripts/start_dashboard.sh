#!/bin/bash
# BLOOMY - Dashboard startup script

cd "$(dirname "$0")"

# Activar entorno virtual si existe, sino crearlo
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Instalando dependencias..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Iniciar dashboard
echo "🚀 Iniciando BLOOMY dashboard..."
echo "🌐 Accede en: http://127.0.0.1:8050"
python app.py
