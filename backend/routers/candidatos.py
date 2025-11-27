from fastapi import APIRouter, HTTPException
from backend.core.db import get_db_connection
from backend.schemas import (
    CandidatoPresidencialCreate,
    CandidatoRegionalCreate,
    CandidatoDistritalCreate,
)

router = APIRouter(prefix="/api/candidatos", tags=["candidatos"])

@router.get("/presidenciales")
async def get_candidatos_presidenciales():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_CANDIDATO_PRESIDENCIAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_PRESIDENCIAL")
        rows = cursor.fetchall()
        candidatos = []
        for row in rows:
            candidatos.append({"id": row[0], "nombres": row[1], "apellidos": row[2], "nombre_completo": f"{row[1]} {row[2]}", "cantidad_votos": row[3] or 0})
        return candidatos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/regionales")
async def get_candidatos_regionales():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_CANDIDATO_REGIONAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_REGIONAL")
        rows = cursor.fetchall()
        candidatos = []
        for row in rows:
            candidatos.append({"id": row[0], "nombres": row[1], "apellidos": row[2], "nombre_completo": f"{row[1]} {row[2]}", "cantidad_votos": row[3] or 0})
        return candidatos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/distritales")
async def get_candidatos_distritales():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_CANDIDATO_DISTRITAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_DISTRITAL")
        rows = cursor.fetchall()
        candidatos = []
        for row in rows:
            candidatos.append({"id": row[0], "nombres": row[1], "apellidos": row[2], "nombre_completo": f"{row[1]} {row[2]}", "cantidad_votos": row[3] or 0})
        return candidatos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/presidenciales")
async def create_candidato_presidencial(candidato: CandidatoPresidencialCreate):
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
        return {"id": id_candidato, "nombres": candidato.nombres, "apellidos": candidato.apellidos, "message": "Candidato presidencial creado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/regionales")
async def create_candidato_regional(candidato: CandidatoRegionalCreate):
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
        return {"id": id_candidato, "nombres": candidato.nombres, "apellidos": candidato.apellidos, "message": "Candidato regional creado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/distritales")
async def create_candidato_distrital(candidato: CandidatoDistritalCreate):
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
        return {"id": id_candidato, "nombres": candidato.nombres, "apellidos": candidato.apellidos, "message": "Candidato distrital creado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

