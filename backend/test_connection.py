"""Script para probar la conexión a SQL Server"""
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "DESKTOP-9HF4IO3\\PC")
DB_DATABASE = os.getenv("DB_DATABASE", "SISTEMA_ELECTORAL")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "true").lower() == "true"

print(f"Intentando conectar a: {DB_SERVER}")
print(f"Base de datos: {DB_DATABASE}")
print(f"Autenticación Windows: {DB_TRUSTED_CONNECTION}")

try:
    if DB_TRUSTED_CONNECTION:
        connection_string = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    else:
        DB_USER = os.getenv("DB_USER", "")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        connection_string = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
            "TrustServerCertificate=yes;"
        )
    
    print(f"\nCadena de conexión: {connection_string}")
    print("\nConectando...")
    
    conn = pyodbc.connect(connection_string)
    print("OK: Conexion exitosa a SQL Server!")
    
    # Probar una consulta simple
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()
    print(f"\nVersion de SQL Server: {version[0][:50]}...")
    
    # Verificar si la base de datos existe
    cursor.execute("SELECT name FROM sys.databases WHERE name = ?", DB_DATABASE)
    db_exists = cursor.fetchone()
    if db_exists:
        print(f"OK: Base de datos '{DB_DATABASE}' encontrada")
    else:
        print(f"ADVERTENCIA: Base de datos '{DB_DATABASE}' NO encontrada")
    
    conn.close()
    print("\nOK: Prueba de conexion completada exitosamente!")
    
except Exception as e:
    print(f"\nERROR: Error de conexion: {str(e)}")
    print("\nPosibles soluciones:")
    print("1. Verifica que SQL Server este corriendo")
    print("2. Verifica que el nombre del servidor sea correcto")
    print("3. Verifica que la instancia este correcta (DESKTOP-9HF4IO3\\PC)")
    print("4. Verifica que SQL Server permita conexiones remotas")
    print("5. Prueba conectarte con SQL Server Management Studio primero")
    print("\nOpciones alternativas para DB_SERVER:")
    print("- localhost")
    print("- localhost\\SQLEXPRESS")
    print("- . (punto)")
    print("- DESKTOP-9HF4IO3 (sin instancia)")

