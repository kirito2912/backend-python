"""
Script para corregir el hash del admin en la base de datos
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
    
    # Calcular el hash correcto de "12345"
    correct_hash = hash_password("12345")
    print(f"Hash correcto de '12345': {correct_hash}")
    print(f"Longitud: {len(correct_hash)} caracteres")
    print()
    
    # Actualizar el hash en la base de datos
    cursor.execute(
        "UPDATE USUARIO SET CONTRASENA = ? WHERE CORREO = ?",
        (correct_hash, 'admin@grupo3.com')
    )
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"[OK] Hash actualizado correctamente para admin@grupo3.com")
        print()
        
        # Verificar que se actualizó correctamente
        cursor.execute("SELECT CORREO, CONTRASENA FROM USUARIO WHERE CORREO = ?", ('admin@grupo3.com',))
        row = cursor.fetchone()
        if row:
            print(f"Verificación:")
            print(f"  Correo: {row[0]}")
            print(f"  Hash almacenado: {row[1]}")
            print(f"  Longitud: {len(row[1])} caracteres")
            print(f"  ¿Coincide? {row[1] == correct_hash}")
    else:
        print("⚠ No se encontró el usuario admin@grupo3.com para actualizar")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

