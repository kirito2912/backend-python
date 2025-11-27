"""Script para probar diferentes formatos de conexión a SQL Server"""
import pyodbc

# Diferentes formatos a probar
server_formats = [
    "DESKTOP-9HF4IO3\\PC",
    "DESKTOP-9HF4IO3",
    "localhost",
    "localhost\\SQLEXPRESS",
    ".",
    "(local)",
    "127.0.0.1"
]

DB_DATABASE = "SISTEMA_ELECTORAL"
DB_DRIVER = "ODBC Driver 17 for SQL Server"

print("Probando diferentes formatos de conexion...\n")

for server in server_formats:
    try:
        connection_string = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={server};"
            f"DATABASE={DB_DATABASE};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        print(f"Probando: {server}...", end=" ")
        conn = pyodbc.connect(connection_string, timeout=3)
        print("OK - Conexion exitosa!")
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        print(f"  Version: {version[0][:60]}...")
        conn.close()
        print(f"\nFORMATO CORRECTO: {server}\n")
        break
    except Exception as e:
        print(f"FALLO - {str(e)[:80]}...")
        continue

print("\nSi ninguno funciono, verifica:")
print("1. SQL Server esta corriendo")
print("2. SQL Server Browser esta corriendo")
print("3. La instancia existe y esta configurada correctamente")

