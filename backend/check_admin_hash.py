"""
Script para verificar el hash del admin en la base de datos
"""
import pyodbc
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_DATABASE = os.getenv("DB_DATABASE", "SISTEMA_ELECTORAL")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "true").lower() == "true"

def get_db_connection():
    """Crea una conexión a SQL Server"""
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
    return pyodbc.connect(connection_string)

def hash_password(password: str) -> str:
    """Hashea una contraseña usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscar el admin
    cursor.execute("SELECT ID_USUARIO, CORREO, CONTRASENA, ROL FROM USUARIO WHERE CORREO = ?", ('admin@grupo3.com',))
    row = cursor.fetchone()
    
    if row:
        print(f"Usuario encontrado:")
        print(f"  ID: {row[0]}")
        print(f"  Correo: {row[1]}")
        print(f"  Hash almacenado: {row[2]}")
        print(f"  Longitud del hash: {len(row[2])}")
        print(f"  Rol: {row[3]}")
        print()
        
        # Calcular el hash de "12345"
        expected_hash = hash_password("12345")
        print(f"Hash esperado de '12345': {expected_hash}")
        print(f"Longitud del hash esperado: {len(expected_hash)}")
        print()
        
        # Comparar
        stored_hash = row[2].strip()
        print(f"Hash almacenado (sin espacios): {stored_hash}")
        print(f"¿Coinciden? {stored_hash.lower() == expected_hash.lower()}")
        print()
        
        # Mostrar diferencias byte por byte
        if stored_hash.lower() != expected_hash.lower():
            print("Comparación byte por byte:")
            for i, (s, e) in enumerate(zip(stored_hash.lower(), expected_hash.lower())):
                if s != e:
                    print(f"  Diferencia en posición {i}: '{s}' vs '{e}'")
                    if i > 10:
                        print("  ... (mostrando solo las primeras diferencias)")
                        break
    else:
        print("Usuario admin@grupo3.com no encontrado en la base de datos")
        print()
        print("Usuarios en la base de datos:")
        cursor.execute("SELECT ID_USUARIO, CORREO, ROL FROM USUARIO")
        for r in cursor.fetchall():
            print(f"  - {r[1]} ({r[2]})")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

