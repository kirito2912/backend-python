"""Script para crear candidatos de ejemplo en la base de datos"""
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_DATABASE = os.getenv("DB_DATABASE", "SISTEMA_ELECTORAL")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "true").lower() == "true"

print("Conectando a la base de datos...")

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
    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    print("OK: Conectado a la base de datos")
    
    # Candidatos Presidenciales
    print("\nCreando candidatos presidenciales...")
    candidatos_presidenciales = [
        ("Keiko", "Fujimori"),
        ("Rafael", "Lopez Aliaga"),
        ("Cesar", "Acuna")
    ]
    
    for nombres, apellidos in candidatos_presidenciales:
        try:
            cursor.execute(
                """INSERT INTO CANDIDATO_PRESIDENCIAL (NOMBRES, APELLIDOS, CANTIDAD_VOTOS)
                   VALUES (?, ?, 0)""",
                (nombres, apellidos)
            )
            print(f"  OK: {nombres} {apellidos}")
        except Exception as e:
            if "PRIMARY KEY" in str(e) or "duplicate" in str(e).lower():
                print(f"  Ya existe: {nombres} {apellidos}")
            else:
                print(f"  Error: {nombres} {apellidos} - {str(e)}")
    
    # Candidatos Regionales
    print("\nCreando candidatos regionales...")
    candidatos_regionales = [
        ("Ana Maria", "Torres"),
        ("Miguel Angel", "Castro"),
        ("Laura", "Mendoza")
    ]
    
    for nombres, apellidos in candidatos_regionales:
        try:
            cursor.execute(
                """INSERT INTO CANDIDATO_REGIONAL (NOMBRES, APELLIDOS, CANTIDAD_VOTOS)
                   VALUES (?, ?, 0)""",
                (nombres, apellidos)
            )
            print(f"  OK: {nombres} {apellidos}")
        except Exception as e:
            if "PRIMARY KEY" in str(e) or "duplicate" in str(e).lower():
                print(f"  Ya existe: {nombres} {apellidos}")
            else:
                print(f"  Error: {nombres} {apellidos} - {str(e)}")
    
    # Candidatos Distritales
    print("\nCreando candidatos distritales...")
    candidatos_distritales = [
        ("Carlos", "Rojas"),
        ("Patricia", "Silva"),
        ("Javier", "Quispe")
    ]
    
    for nombres, apellidos in candidatos_distritales:
        try:
            cursor.execute(
                """INSERT INTO CANDIDATO_DISTRITAL (NOMBRES, APELLIDOS, CANTIDAD_VOTOS)
                   VALUES (?, ?, 0)""",
                (nombres, apellidos)
            )
            print(f"  OK: {nombres} {apellidos}")
        except Exception as e:
            if "PRIMARY KEY" in str(e) or "duplicate" in str(e).lower():
                print(f"  Ya existe: {nombres} {apellidos}")
            else:
                print(f"  Error: {nombres} {apellidos} - {str(e)}")
    
    conn.commit()
    print("\nOK: Todos los candidatos creados exitosamente!")
    
    # Mostrar resumen
    cursor.execute("SELECT COUNT(*) FROM CANDIDATO_PRESIDENCIAL")
    pres_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM CANDIDATO_REGIONAL")
    reg_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM CANDIDATO_DISTRITAL")
    dist_count = cursor.fetchone()[0]
    
    print(f"\nResumen:")
    print(f"  Presidenciales: {pres_count}")
    print(f"  Regionales: {reg_count}")
    print(f"  Distritales: {dist_count}")
    
    conn.close()
    
except Exception as e:
    print(f"\nERROR: {str(e)}")

