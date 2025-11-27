import os
import hashlib
import pyodbc

DB_SERVER = os.getenv("DB_SERVER", "DESKTOP-9HF4IO3\\PC")
DB_DATABASE = os.getenv("DB_DATABASE", "SISTEMA_ELECTORAL")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "true").lower() == "true"

def get_db_connection():
    if DB_TRUSTED_CONNECTION:
        connection_string = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    else:
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
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

