@echo off
echo ====================================
echo   Iniciando Backend Sistema Electoral
echo ====================================
echo.

REM Verificar si existe el archivo .env
if not exist .env (
    echo [ERROR] No se encontro el archivo .env
    echo Por favor crea el archivo .env con las credenciales de SQL Server
    echo.
    echo Ejemplo:
    echo DB_SERVER=localhost
    echo DB_DATABASE=SISTEMA_ELECTORAL
    echo DB_USER=sa
    echo DB_PASSWORD=tu_contraseña
    echo DB_DRIVER=ODBC Driver 17 for SQL Server
    echo.
    pause
    exit /b 1
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
python -m uvicorn main:app --reload --port 8000

pause

