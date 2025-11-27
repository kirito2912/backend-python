# Backend - Sistema Electoral

Backend FastAPI para el Sistema Electoral conectado a SQL Server.

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales de SQL Server
```

3. Asegúrate de tener instalado el driver ODBC de SQL Server:
   - Windows: Generalmente viene preinstalado
   - Linux/Mac: Instalar `unixodbc` y el driver correspondiente

## Ejecutar el servidor

```bash
uvicorn main:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`

## Documentación de la API

Una vez que el servidor esté corriendo, puedes acceder a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints principales

- `/api/auth/login` - Autenticación de usuarios
- `/api/votantes` - Gestión de votantes
- `/api/candidatos/*` - Gestión de candidatos
- `/api/votos/*` - Registro de votos
- `/api/resultados/*` - Consulta de resultados
- `/api/results/*` - Resultados para panel administrativo
- `/api/processing/*` - Procesamiento de datos
- `/api/analysis/*` - Análisis estadístico

