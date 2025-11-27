"""
Backend FastAPI para Sistema Electoral
Conectado a SQL Server
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date
import pyodbc
import os
from dotenv import load_dotenv
import hashlib
import secrets

load_dotenv()

app = FastAPI(title="Sistema Electoral API", version="1.0.0")

# Configurar CORS - Permitir todos los orígenes de localhost en desarrollo
import re

def is_localhost_origin(origin: str) -> bool:
    """Verifica si el origen es localhost o 127.0.0.1"""
    if not origin:
        return False
    localhost_patterns = [
        r"^http://localhost:\d+$",
        r"^http://127\.0\.0\.1:\d+$",
        r"^http://localhost$",
        r"^http://127\.0\.0\.1$",
    ]
    return any(re.match(pattern, origin) for pattern in localhost_patterns)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?$",  # Permite cualquier puerto de localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de conexión a SQL Server
DB_SERVER = os.getenv("DB_SERVER", "DESKTOP-9HF4IO3\\PC")
DB_DATABASE = os.getenv("DB_DATABASE", "SISTEMA_ELECTORAL")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "true").lower() == "true"

def get_db_connection():
    """Crea una conexión a SQL Server"""
    try:
        if DB_TRUSTED_CONNECTION:
            # Usar autenticación de Windows (Trusted Connection)
            connection_string = (
                f"DRIVER={{{DB_DRIVER}}};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_DATABASE};"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )
        else:
            # Usar autenticación con usuario y contraseña
            connection_string = (
                f"DRIVER={{{DB_DRIVER}}};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_DATABASE};"
                f"UID={DB_USER};"
                f"PWD={DB_PASSWORD};"
                "TrustServerCertificate=yes;"
            )
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión a la base de datos: {str(e)}"
        )

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasena: str

class UsuarioCreate(BaseModel):
    correo: EmailStr
    contrasena: str
    rol: str = "usuario"

class VotanteCreate(BaseModel):
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    region: str
    distrito: str

class CandidatoPresidencialCreate(BaseModel):
    nombres: str
    apellidos: str

class CandidatoRegionalCreate(BaseModel):
    nombres: str
    apellidos: str

class CandidatoDistritalCreate(BaseModel):
    nombres: str
    apellidos: str

class VotoPresidencialCreate(BaseModel):
    id_votantes: int
    id_candidato: int

class VotoRegionalCreate(BaseModel):
    id_votantes: int
    id_candidato_regional: int
    region: str

class VotoDistritalCreate(BaseModel):
    id_votantes: int
    id_candidato_distrital: int
    distrito: str

class VotanteStatus(BaseModel):
    can_vote_presidencial: bool
    can_vote_regional: bool
    can_vote_distrital: bool
    has_all_votes: bool

class VotoNuloCreate(BaseModel):
    id_votantes: int
    dni: str

# ============================================================================
# UTILIDADES
# ============================================================================

def hash_password(password: str) -> str:
    """Hashea una contraseña usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verifica una contraseña"""
    return hash_password(password) == hashed

# ============================================================================
# ENDPOINTS DE AUTENTICACIÓN
# ============================================================================

@app.post("/api/auth/login")
async def login(usuario: UsuarioLogin):
    """Autentica un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Primero buscar el usuario por correo
        cursor.execute(
            "SELECT ID_USUARIO, CORREO, CONTRASENA, ROL FROM USUARIO WHERE CORREO = ?",
            (usuario.correo,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Obtener el hash almacenado y limpiarlo de espacios
        stored_hash = row[2].strip() if row[2] else ""
        hashed_password = hash_password(usuario.contrasena)
        
        # Comparar los hashes
        if stored_hash.lower() != hashed_password.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        return {
            "id_usuario": row[0],
            "correo": row[1],
            "rol": row[3],
            "message": "Login exitoso"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/auth/register")
async def register(usuario: UsuarioCreate):
    """Registra un nuevo usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si el correo ya existe
        cursor.execute("SELECT ID_USUARIO FROM USUARIO WHERE CORREO = ?", (usuario.correo,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El correo ya está registrado"
            )
        
        hashed_password = hash_password(usuario.contrasena)
        cursor.execute(
            "INSERT INTO USUARIO (CORREO, CONTRASENA, ROL) OUTPUT INSERTED.ID_USUARIO VALUES (?, ?, ?)",
            (usuario.correo, hashed_password, usuario.rol)
        )
        id_usuario = cursor.fetchone()[0]
        conn.commit()
        
        return {
            "id_usuario": id_usuario,
            "correo": usuario.correo,
            "rol": usuario.rol,
            "message": "Usuario registrado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# ENDPOINTS DE VOTANTES
# ============================================================================

@app.post("/api/votantes")
async def create_votante(votante: VotanteCreate):
    """Registra un nuevo votante"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si el DNI ya existe
        cursor.execute("SELECT ID_VOTANTES FROM VOTANTES WHERE DNI = ?", (votante.dni,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El DNI ya está registrado"
            )
        
        cursor.execute(
            """INSERT INTO VOTANTES (DNI, NOMBRES, APELLIDOS, FECHA_NACIMIENTO, REGION, DISTRITO)
               OUTPUT INSERTED.ID_VOTANTES VALUES (?, ?, ?, ?, ?, ?)""",
            (votante.dni, votante.nombres, votante.apellidos, votante.fecha_nacimiento,
             votante.region, votante.distrito)
        )
        id_votantes = cursor.fetchone()[0]
        conn.commit()
        
        return {
            "id_votantes": id_votantes,
            "message": "Votante registrado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/votantes/{dni}")
async def get_votante_by_dni(dni: str):
    """Obtiene un votante por DNI"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT ID_VOTANTES, DNI, NOMBRES, APELLIDOS, FECHA_NACIMIENTO, REGION, DISTRITO, FECHA_VOTO
               FROM VOTANTES WHERE DNI = ?""",
            (dni,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Votante no encontrado")
        
        return {
            "id_votantes": row[0],
            "dni": row[1],
            "nombres": row[2],
            "apellidos": row[3],
            "fecha_nacimiento": str(row[4]),
            "region": row[5],
            "distrito": row[6],
            "fecha_voto": str(row[7]) if row[7] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/votantes/{dni}/status", response_model=VotanteStatus)
async def get_votante_status(dni: str):
    """Devuelve el estado de voto de un votante por DNI"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Buscar votante por DNI
        cursor.execute(
            "SELECT ID_VOTANTES FROM VOTANTES WHERE DNI = ?",
            (dni,)
        )
        row = cursor.fetchone()

        if not row:
            # No existe votante: puede votar en todas las categorías
            return VotanteStatus(
                can_vote_presidencial=True,
                can_vote_regional=True,
                can_vote_distrital=True,
                has_all_votes=False
            )

        id_votantes = row[0]

        # Contar votos por categoría
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_PRESIDENCIAL WHERE ID_VOTANTES = ?",
            (id_votantes,)
        )
        votos_presidenciales = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_REGIONAL WHERE ID_VOTANTES = ?",
            (id_votantes,)
        )
        votos_regionales = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_DISTRITAL WHERE ID_VOTANTES = ?",
            (id_votantes,)
        )
        votos_distritales = cursor.fetchone()[0] or 0

        can_vote_presidencial = votos_presidenciales < 1
        can_vote_regional = votos_regionales < 1
        can_vote_distrital = votos_distritales < 1
        has_all_votes = (
            votos_presidenciales >= 1 and
            votos_regionales >= 1 and
            votos_distritales >= 1
        )

        return VotanteStatus(
            can_vote_presidencial=can_vote_presidencial,
            can_vote_regional=can_vote_regional,
            can_vote_distrital=can_vote_distrital,
            has_all_votes=has_all_votes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/votantes")
async def get_all_votantes(limit: int = 100, offset: int = 0):
    """Obtiene todos los votantes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT ID_VOTANTES, DNI, NOMBRES, APELLIDOS, FECHA_NACIMIENTO, REGION, DISTRITO
               FROM VOTANTES ORDER BY ID_VOTANTES DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY""",
            (offset, limit)
        )
        rows = cursor.fetchall()
        
        votantes = []
        for row in rows:
            votantes.append({
                "id_votantes": row[0],
                "dni": row[1],
                "nombres": row[2],
                "apellidos": row[3],
                "fecha_nacimiento": str(row[4]),
                "region": row[5],
                "distrito": row[6]
            })
        
        return votantes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# ENDPOINTS DE CANDIDATOS
# ============================================================================

@app.get("/api/candidatos/presidenciales")
async def get_candidatos_presidenciales():
    """Obtiene todos los candidatos presidenciales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT ID_CANDIDATO_PRESIDENCIAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_PRESIDENCIAL"
        )
        rows = cursor.fetchall()
        
        candidatos = []
        for row in rows:
            candidatos.append({
                "id": row[0],
                "nombres": row[1],
                "apellidos": row[2],
                "nombre_completo": f"{row[1]} {row[2]}",
                "cantidad_votos": row[3] or 0
            })
        
        return candidatos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/candidatos/regionales")
async def get_candidatos_regionales():
    """Obtiene todos los candidatos regionales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT ID_CANDIDATO_REGIONAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_REGIONAL"
        )
        rows = cursor.fetchall()
        
        candidatos = []
        for row in rows:
            candidatos.append({
                "id": row[0],
                "nombres": row[1],
                "apellidos": row[2],
                "nombre_completo": f"{row[1]} {row[2]}",
                "cantidad_votos": row[3] or 0
            })
        
        return candidatos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/candidatos/distritales")
async def get_candidatos_distritales():
    """Obtiene todos los candidatos distritales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT ID_CANDIDATO_DISTRITAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_DISTRITAL"
        )
        rows = cursor.fetchall()
        
        candidatos = []
        for row in rows:
            candidatos.append({
                "id": row[0],
                "nombres": row[1],
                "apellidos": row[2],
                "nombre_completo": f"{row[1]} {row[2]}",
                "cantidad_votos": row[3] or 0
            })
        
        return candidatos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/candidatos/presidenciales")
async def create_candidato_presidencial(candidato: CandidatoPresidencialCreate):
    """Crea un nuevo candidato presidencial"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """INSERT INTO CANDIDATO_PRESIDENCIAL (NOMBRES, APELLIDOS)
               OUTPUT INSERTED.ID_CANDIDATO_PRESIDENCIAL VALUES (?, ?)""",
            (candidato.nombres, candidato.apellidos)
        )
        id_candidato = cursor.fetchone()[0]
        conn.commit()
        
        return {
            "id": id_candidato,
            "nombres": candidato.nombres,
            "apellidos": candidato.apellidos,
            "message": "Candidato presidencial creado exitosamente"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/candidatos/regionales")
async def create_candidato_regional(candidato: CandidatoRegionalCreate):
    """Crea un nuevo candidato regional"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """INSERT INTO CANDIDATO_REGIONAL (NOMBRES, APELLIDOS)
               OUTPUT INSERTED.ID_CANDIDATO_REGIONAL VALUES (?, ?)""",
            (candidato.nombres, candidato.apellidos)
        )
        id_candidato = cursor.fetchone()[0]
        conn.commit()
        
        return {
            "id": id_candidato,
            "nombres": candidato.nombres,
            "apellidos": candidato.apellidos,
            "message": "Candidato regional creado exitosamente"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/candidatos/distritales")
async def create_candidato_distrital(candidato: CandidatoDistritalCreate):
    """Crea un nuevo candidato distrital"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """INSERT INTO CANDIDATO_DISTRITAL (NOMBRES, APELLIDOS)
               OUTPUT INSERTED.ID_CANDIDATO_DISTRITAL VALUES (?, ?)""",
            (candidato.nombres, candidato.apellidos)
        )
        id_candidato = cursor.fetchone()[0]
        conn.commit()
        
        return {
            "id": id_candidato,
            "nombres": candidato.nombres,
            "apellidos": candidato.apellidos,
            "message": "Candidato distrital creado exitosamente"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# ENDPOINTS DE VOTOS
# ============================================================================

@app.post("/api/votos/presidencial")
async def create_voto_presidencial(voto: VotoPresidencialCreate):
    """Registra un voto presidencial"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si el votante existe
        cursor.execute(
            "SELECT ID_VOTANTES FROM VOTANTES WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votante = cursor.fetchone()
        
        if not votante:
            raise HTTPException(status_code=404, detail="Votante no encontrado")
        
        # Verificar si el votante ya emitió los tres tipos de voto
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_PRESIDENCIAL WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votos_presidenciales = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_REGIONAL WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votos_regionales = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_DISTRITAL WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votos_distritales = cursor.fetchone()[0] or 0
        
        if votos_presidenciales >= 1 and votos_regionales >= 1 and votos_distritales >= 1:
            raise HTTPException(
                status_code=400,
                detail="El votante ya ha ejercido todos sus votos (presidencial, regional y distrital)"
            )

        # Verificar si ya votó presidencial
        if votos_presidenciales >= 1:
            raise HTTPException(
                status_code=400,
                detail="El votante ya ha ejercido su voto presidencial"
            )
        
        # Obtener datos del candidato
        cursor.execute(
            "SELECT NOMBRES, APELLIDOS FROM CANDIDATO_PRESIDENCIAL WHERE ID_CANDIDATO_PRESIDENCIAL = ?",
            (voto.id_candidato,)
        )
        candidato = cursor.fetchone()
        
        if not candidato:
            raise HTTPException(status_code=404, detail="Candidato no encontrado")
        
        # Registrar el voto
        cursor.execute(
            """INSERT INTO VOTO_PRESIDENCIAL (ID_VOTANTES, ID_CANDIDATO, NOMBRE, APELLIDO)
               VALUES (?, ?, ?, ?)""",
            (voto.id_votantes, voto.id_candidato, candidato[0], candidato[1])
        )
        
        # Actualizar cantidad de votos del candidato
        cursor.execute(
            "UPDATE CANDIDATO_PRESIDENCIAL SET CANTIDAD_VOTOS = CANTIDAD_VOTOS + 1 WHERE ID_CANDIDATO_PRESIDENCIAL = ?",
            (voto.id_candidato,)
        )
        
        # Actualizar votante
        cursor.execute(
            "UPDATE VOTANTES SET FECHA_VOTO = ? WHERE ID_VOTANTES = ?",
            (datetime.now(), voto.id_votantes)
        )
        
        conn.commit()
        
        return {
            "message": "Voto presidencial registrado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/votos/regional")
async def create_voto_regional(voto: VotoRegionalCreate):
    """Registra un voto regional"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que el votante existe
        cursor.execute(
            "SELECT ID_VOTANTES FROM VOTANTES WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votante = cursor.fetchone()
        
        if not votante:
            raise HTTPException(status_code=404, detail="Votante no encontrado")

        # Verificar si el votante ya emitió los tres tipos de voto
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_PRESIDENCIAL WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votos_presidenciales = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_REGIONAL WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votos_regionales = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_DISTRITAL WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votos_distritales = cursor.fetchone()[0] or 0
        if votos_presidenciales >= 1 and votos_regionales >= 1 and votos_distritales >= 1:
            raise HTTPException(
                status_code=400,
                detail="El votante ya ha ejercido todos sus votos (presidencial, regional y distrital)"
            )

        # Verificar si ya votó regional (solo se permite un voto regional)
        if votos_regionales >= 1:
            raise HTTPException(
                status_code=400,
                detail="El votante ya ha ejercido su voto regional"
            )
        
        # Obtener datos del candidato
        cursor.execute(
            "SELECT NOMBRES, APELLIDOS FROM CANDIDATO_REGIONAL WHERE ID_CANDIDATO_REGIONAL = ?",
            (voto.id_candidato_regional,)
        )
        candidato = cursor.fetchone()
        
        if not candidato:
            raise HTTPException(status_code=404, detail="Candidato regional no encontrado")
        
        # Verificar si ya votó regional (opcional - depende de las reglas de negocio)
        # Por ahora permitimos múltiples votos regionales si es necesario
        
        # Registrar el voto
        cursor.execute(
            """INSERT INTO VOTO_REGIONAL (ID_VOTANTES, ID_CANDIDATO_REGIONAL, NOMBRE, APELLIDO)
               VALUES (?, ?, ?, ?)""",
            (voto.id_votantes, voto.id_candidato_regional, candidato[0], candidato[1])
        )
        
        # Actualizar cantidad de votos del candidato
        cursor.execute(
            "UPDATE CANDIDATO_REGIONAL SET CANTIDAD_VOTOS = CANTIDAD_VOTOS + 1 WHERE ID_CANDIDATO_REGIONAL = ?",
            (voto.id_candidato_regional,)
        )
        
        conn.commit()
        
        return {
            "message": "Voto regional registrado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/votos/distrital")
async def create_voto_distrital(voto: VotoDistritalCreate):
    """Registra un voto distrital"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que el votante existe
        cursor.execute(
            "SELECT ID_VOTANTES FROM VOTANTES WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votante = cursor.fetchone()
        
        if not votante:
            raise HTTPException(status_code=404, detail="Votante no encontrado")

        # Verificar si el votante ya emitió los tres tipos de voto
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_PRESIDENCIAL WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votos_presidenciales = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_REGIONAL WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votos_regionales = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(*) FROM VOTO_DISTRITAL WHERE ID_VOTANTES = ?",
            (voto.id_votantes,)
        )
        votos_distritales = cursor.fetchone()[0] or 0
        if votos_presidenciales >= 1 and votos_regionales >= 1 and votos_distritales >= 1:
            raise HTTPException(
                status_code=400,
                detail="El votante ya ha ejercido todos sus votos (presidencial, regional y distrital)"
            )

        # Verificar si ya votó distrital (solo se permite un voto distrital)
        if votos_distritales >= 1:
            raise HTTPException(
                status_code=400,
                detail="El votante ya ha ejercido su voto distrital"
            )
        
        # Obtener datos del candidato
        cursor.execute(
            "SELECT NOMBRES, APELLIDOS FROM CANDIDATO_DISTRITAL WHERE ID_CANDIDATO_DISTRITAL = ?",
            (voto.id_candidato_distrital,)
        )
        candidato = cursor.fetchone()
        
        if not candidato:
            raise HTTPException(status_code=404, detail="Candidato distrital no encontrado")
        
        # Verificar si ya votó distrital (opcional - depende de las reglas de negocio)
        # Por ahora permitimos múltiples votos distritales si es necesario
        
        # Registrar el voto
        cursor.execute(
            """INSERT INTO VOTO_DISTRITAL (ID_VOTANTES, ID_CANDIDATO_DISTRITAL, NOMBRE, APELLIDO)
               VALUES (?, ?, ?, ?)""",
            (voto.id_votantes, voto.id_candidato_distrital, candidato[0], candidato[1])
        )
        
        # Actualizar cantidad de votos del candidato
        cursor.execute(
            "UPDATE CANDIDATO_DISTRITAL SET CANTIDAD_VOTOS = CANTIDAD_VOTOS + 1 WHERE ID_CANDIDATO_DISTRITAL = ?",
            (voto.id_candidato_distrital,)
        )
        
        conn.commit()
        
        return {
            "message": "Voto distrital registrado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/votos/nulo")
async def create_voto_nulo(voto: VotoNuloCreate):
    """Registra un voto nulo"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO VOTO_NULO (ID_VOTANTES, DNI) VALUES (?, ?)",
            (voto.id_votantes, voto.dni)
        )
        
        # Actualizar votante
        cursor.execute(
            "UPDATE VOTANTES SET FECHA_VOTO = ? WHERE ID_VOTANTES = ?",
            (datetime.now(), voto.id_votantes)
        )
        
        conn.commit()
        
        return {
            "message": "Voto nulo registrado exitosamente"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# ENDPOINTS DE RESULTADOS
# ============================================================================

@app.get("/api/resultados/presidencial")
async def get_resultados_presidencial():
    """Obtiene los resultados presidenciales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT ID_CANDIDATO_PRESIDENCIAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS
               FROM CANDIDATO_PRESIDENCIAL
               ORDER BY CANTIDAD_VOTOS DESC"""
        )
        rows = cursor.fetchall()
        
        total_votos = sum(row[3] or 0 for row in rows)
        
        resultados = []
        for row in rows:
            votos = row[3] or 0
            porcentaje = (votos / total_votos * 100) if total_votos > 0 else 0
            resultados.append({
                "id": row[0],
                "nombre": f"{row[1]} {row[2]}",
                "votos": votos,
                "porcentaje": round(porcentaje, 2)
            })
        
        return {
            "total_votos": total_votos,
            "candidatos": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/resultados/regional")
async def get_resultados_regional():
    """Obtiene los resultados regionales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT ID_CANDIDATO_REGIONAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS
               FROM CANDIDATO_REGIONAL
               ORDER BY CANTIDAD_VOTOS DESC"""
        )
        rows = cursor.fetchall()
        
        resultados = []
        for row in rows:
            resultados.append({
                "id": row[0],
                "nombre": f"{row[1]} {row[2]}",
                "votos": row[3] or 0
            })
        
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/resultados/distrital")
async def get_resultados_distrital():
    """Obtiene los resultados distritales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT ID_CANDIDATO_DISTRITAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS
               FROM CANDIDATO_DISTRITAL
               ORDER BY CANTIDAD_VOTOS DESC"""
        )
        rows = cursor.fetchall()
        
        resultados = []
        for row in rows:
            resultados.append({
                "id": row[0],
                "nombre": f"{row[1]} {row[2]}",
                "votos": row[3] or 0
            })
        
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# ENDPOINTS DE RESULTADOS (para el panel administrativo)
# ============================================================================

@app.get("/api/results/status")
async def get_results_status():
    """Obtiene el estado de los datos (NULL/N/A)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Contar votos con NULL
        cursor.execute(
            """SELECT COUNT(*) FROM VOTANTES 
               WHERE FECHA_VOTO IS NULL"""
        )
        null_count = cursor.fetchone()[0] or 0
        
        # Contar total de votos
        cursor.execute("SELECT COUNT(*) FROM VOTANTES WHERE FECHA_VOTO IS NOT NULL")
        total_votes = cursor.fetchone()[0] or 0
        
        return {
            "hasNullData": null_count > 0,
            "nullCount": null_count,
            "naCount": 0,
            "totalVotes": total_votes,
            "lastUpdated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/results/summary")
async def get_results_summary():
    """Obtiene el resumen de resultados electorales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT ID_CANDIDATO_PRESIDENCIAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS
               FROM CANDIDATO_PRESIDENCIAL
               ORDER BY CANTIDAD_VOTOS DESC"""
        )
        rows = cursor.fetchall()
        
        total_votes = sum(row[3] or 0 for row in rows)
        
        candidates = []
        for row in rows:
            votes = row[3] or 0
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            candidates.append({
                "id": row[0],
                "name": f"{row[1]} {row[2]}",
                "votes": votes,
                "percentage": round(percentage, 2)
            })
        
        # Calcular tasa de participación (simplificado)
        cursor.execute("SELECT COUNT(*) FROM VOTANTES")
        total_votantes = cursor.fetchone()[0] or 1
        participation_rate = round((total_votes / total_votantes * 100), 2) if total_votantes > 0 else 0
        
        return {
            "totalVotes": total_votes,
            "candidates": candidates,
            "participationRate": participation_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# ENDPOINTS DE PROCESAMIENTO (simplificados)
# ============================================================================

@app.post("/api/processing/analyze-quality")
async def analyze_quality():
    """Analiza la calidad de los datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Contar registros totales
        cursor.execute("SELECT COUNT(*) FROM VOTANTES")
        total_records = cursor.fetchone()[0] or 0
        
        # Contar NULLs
        cursor.execute(
            """SELECT 
                SUM(CASE WHEN DNI IS NULL THEN 1 ELSE 0 END) as dni_nulls,
                SUM(CASE WHEN NOMBRES IS NULL THEN 1 ELSE 0 END) as nombres_nulls,
                SUM(CASE WHEN FECHA_NACIMIENTO IS NULL THEN 1 ELSE 0 END) as fecha_nulls
               FROM VOTANTES"""
        )
        nulls = cursor.fetchone()
        
        # Contar duplicados (mismo DNI)
        cursor.execute(
            """SELECT COUNT(*) - COUNT(DISTINCT DNI) as duplicates
               FROM VOTANTES WHERE DNI IS NOT NULL"""
        )
        duplicates = cursor.fetchone()[0] or 0
        
        return {
            "totalRecords": total_records,
            "nullCounts": {
                "dni": nulls[0] or 0,
                "nombres": nulls[1] or 0,
                "fecha_nacimiento": nulls[2] or 0
            },
            "duplicateCount": duplicates,
            "dataTypes": {
                "dni": "varchar",
                "nombres": "varchar",
                "fecha_nacimiento": "date"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/processing/status")
async def get_processing_status():
    """Obtiene el estado actual del procesamiento"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM VOTANTES WHERE FECHA_VOTO IS NOT NULL")
        vote_count = cursor.fetchone()[0] or 0
        
        # Ya no tenemos CANDIDATO_VOTADO, así que has_na_data siempre será False
        has_na_data = False
        
        return {
            "voteCount": vote_count,
            "hasNAData": has_na_data,
            "lastProcessed": datetime.now().isoformat(),
            "processingHistory": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# ENDPOINTS DE ANÁLISIS
# ============================================================================

@app.get("/api/analysis/stats")
async def get_analysis_stats():
    """Obtiene estadísticas generales de análisis"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Votantes activos (que han votado hoy)
        today = datetime.now().date()
        cursor.execute(
            """SELECT COUNT(DISTINCT ID_VOTANTES) 
               FROM VOTANTES 
               WHERE CAST(FECHA_VOTO AS DATE) = ?""",
            (today,)
        )
        active_voters = cursor.fetchone()[0] or 0
        
        # Total de votos
        cursor.execute("SELECT COUNT(*) FROM VOTANTES WHERE FECHA_VOTO IS NOT NULL")
        total_votes = cursor.fetchone()[0] or 0
        
        # Tasa de participación
        cursor.execute("SELECT COUNT(*) FROM VOTANTES")
        total_votantes = cursor.fetchone()[0] or 1
        participation_rate = round((total_votes / total_votantes * 100), 2) if total_votantes > 0 else 0
        
        # Hora pico (simplificado)
        peak_activity_time = "14:30"
        
        return {
            "activeVoters": active_voters,
            "participationRate": participation_rate,
            "peakActivityTime": peak_activity_time,
            "totalVotes": total_votes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/analysis/voting-flow")
async def get_voting_flow():
    """Obtiene el flujo de votación por hora"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener votos del día agrupados por hora
        today = datetime.now().date()
        cursor.execute(
            """SELECT DATEPART(HOUR, FECHA_VOTO) as hora, COUNT(*) as votos
               FROM VOTANTES
               WHERE CAST(FECHA_VOTO AS DATE) = ?
               GROUP BY DATEPART(HOUR, FECHA_VOTO)
               ORDER BY hora""",
            (today,)
        )
        rows = cursor.fetchall()
        
        flow_data = []
        for row in rows:
            hour = f"{int(row[0]):02d}:00"
            flow_data.append({
                "hour": hour,
                "votes": row[1]
            })
        
        # Si no hay datos, retornar datos de ejemplo
        if not flow_data:
            flow_data = [
                {"hour": "08:00", "votes": 0},
                {"hour": "09:00", "votes": 0},
                {"hour": "10:00", "votes": 0},
                {"hour": "11:00", "votes": 0},
                {"hour": "12:00", "votes": 0},
                {"hour": "13:00", "votes": 0},
                {"hour": "14:00", "votes": 0},
                {"hour": "15:00", "votes": 0},
                {"hour": "16:00", "votes": 0},
                {"hour": "17:00", "votes": 0}
            ]
        
        return flow_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# ENDPOINTS DE ENTRENAMIENTO ML (simplificados)
# ============================================================================

@app.get("/api/training/stats")
async def get_training_stats():
    """Obtiene estadísticas de votos válidos para entrenamiento"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT COUNT(*) 
               FROM VOTANTES 
               WHERE FECHA_VOTO IS NOT NULL"""
        )
        valid_votes = cursor.fetchone()[0] or 0
        
        # Contar candidatos únicos desde las tablas de votos
        cursor.execute("SELECT COUNT(DISTINCT ID_CANDIDATO) FROM VOTO_PRESIDENCIAL")
        presidencial_candidates = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(DISTINCT ID_CANDIDATO_REGIONAL) FROM VOTO_REGIONAL")
        regional_candidates = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(DISTINCT ID_CANDIDATO_DISTRITAL) FROM VOTO_DISTRITAL")
        distrital_candidates = cursor.fetchone()[0] or 0
        candidates = presidencial_candidates + regional_candidates + distrital_candidates
        
        return {
            "validVotes": valid_votes,
            "candidates": candidates,
            "features": ["Edad", "Educación", "Género"],
            "canTrain": valid_votes >= 10
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

