#!/bin/bash

echo "===================================="
echo "  Iniciando Backend Sistema Electoral"
echo "===================================="
echo ""

# Verificar si existe el archivo .env
if [ ! -f .env ] && [ ! -f config.env ]; then
    echo "[ADVERTENCIA] No se encontró .env ni config.env. Se usarán valores por defecto."
fi

echo "Verificando dependencias..."
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependencias..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudieron instalar las dependencias"
        exit 1
    fi
fi

echo ""
echo "Iniciando servidor en http://localhost:8000"
echo "Presiona Ctrl+C para detener el servidor"
echo ""
python3 -m uvicorn backend.main:app --reload --port 8000

