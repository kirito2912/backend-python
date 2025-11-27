#!/bin/bash

echo "===================================="
echo "  Iniciando Backend Sistema Electoral"
echo "===================================="
echo ""

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo "[ERROR] No se encontró el archivo .env"
    echo "Por favor crea el archivo .env con las credenciales de SQL Server"
    echo ""
    echo "Ejemplo:"
    echo "DB_SERVER=localhost"
    echo "DB_DATABASE=SISTEMA_ELECTORAL"
    echo "DB_USER=sa"
    echo "DB_PASSWORD=tu_contraseña"
    echo "DB_DRIVER=ODBC Driver 17 for SQL Server"
    echo ""
    exit 1
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
python3 -m uvicorn main:app --reload --port 8000

