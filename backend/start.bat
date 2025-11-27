@echo off
echo ====================================
echo   Iniciando Backend Sistema Electoral
echo ====================================
echo.

REM Verificar si existe el archivo .env
if not exist .env if not exist config.env (
    echo [ADVERTENCIA] No se encontro .env ni config.env. Se usaran valores por defecto.
)

echo Verificando dependencias...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

echo.
echo Iniciando servidor en http://localhost:8000
echo Presiona Ctrl+C para detener el servidor
echo.
python -m uvicorn backend.main:app --reload --port 8000

pause

