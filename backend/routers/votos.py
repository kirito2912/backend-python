from fastapi import APIRouter, HTTPException
from backend.core.db import get_db_connection
from backend.schemas import VotoPresidencialCreate, VotoRegionalCreate, VotoDistritalCreate, VotoNuloCreate
from datetime import datetime

router = APIRouter(prefix="/api/votos", tags=["votos"])

@router.post("/presidencial")
async def create_voto_presidencial(voto: VotoPresidencialCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_VOTANTES FROM VOTANTES WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votante = cursor.fetchone()
        if not votante:
            raise HTTPException(status_code=404, detail="Votante no encontrado")
        cursor.execute("SELECT COUNT(*) FROM VOTO_PRESIDENCIAL WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votos_presidenciales = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTO_REGIONAL WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votos_regionales = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTO_DISTRITAL WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votos_distritales = cursor.fetchone()[0] or 0
        if votos_presidenciales >= 1 and votos_regionales >= 1 and votos_distritales >= 1:
            raise HTTPException(status_code=400, detail="El votante ya ha ejercido todos sus votos (presidencial, regional y distrital)")
        if votos_presidenciales >= 1:
            raise HTTPException(status_code=400, detail="El votante ya ha ejercido su voto presidencial")
        cursor.execute("SELECT NOMBRES, APELLIDOS FROM CANDIDATO_PRESIDENCIAL WHERE ID_CANDIDATO_PRESIDENCIAL = ?", (voto.id_candidato,))
        candidato = cursor.fetchone()
        if not candidato:
            raise HTTPException(status_code=404, detail="Candidato no encontrado")
        cursor.execute(
            """INSERT INTO VOTO_PRESIDENCIAL (ID_VOTANTES, ID_CANDIDATO, NOMBRE, APELLIDO)
               VALUES (?, ?, ?, ?)""",
            (voto.id_votantes, voto.id_candidato, candidato[0], candidato[1])
        )
        cursor.execute(
            "UPDATE CANDIDATO_PRESIDENCIAL SET CANTIDAD_VOTOS = CANTIDAD_VOTOS + 1 WHERE ID_CANDIDATO_PRESIDENCIAL = ?",
            (voto.id_candidato,)
        )
        cursor.execute("UPDATE VOTANTES SET FECHA_VOTO = ? WHERE ID_VOTANTES = ?", (datetime.now(), voto.id_votantes))
        conn.commit()
        return {"message": "Voto presidencial registrado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/regional")
async def create_voto_regional(voto: VotoRegionalCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_VOTANTES FROM VOTANTES WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votante = cursor.fetchone()
        if not votante:
            raise HTTPException(status_code=404, detail="Votante no encontrado")
        cursor.execute("SELECT COUNT(*) FROM VOTO_PRESIDENCIAL WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votos_presidenciales = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTO_REGIONAL WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votos_regionales = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTO_DISTRITAL WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votos_distritales = cursor.fetchone()[0] or 0
        if votos_presidenciales >= 1 and votos_regionales >= 1 and votos_distritales >= 1:
            raise HTTPException(status_code=400, detail="El votante ya ha ejercido todos sus votos (presidencial, regional y distrital)")
        if votos_regionales >= 1:
            raise HTTPException(status_code=400, detail="El votante ya ha ejercido su voto regional")
        cursor.execute("SELECT NOMBRES, APELLIDOS FROM CANDIDATO_REGIONAL WHERE ID_CANDIDATO_REGIONAL = ?", (voto.id_candidato_regional,))
        candidato = cursor.fetchone()
        if not candidato:
            raise HTTPException(status_code=404, detail="Candidato regional no encontrado")
        cursor.execute(
            """INSERT INTO VOTO_REGIONAL (ID_VOTANTES, ID_CANDIDATO_REGIONAL, NOMBRE, APELLIDO)
               VALUES (?, ?, ?, ?)""",
            (voto.id_votantes, voto.id_candidato_regional, candidato[0], candidato[1])
        )
        cursor.execute(
            "UPDATE CANDIDATO_REGIONAL SET CANTIDAD_VOTOS = CANTIDAD_VOTOS + 1 WHERE ID_CANDIDATO_REGIONAL = ?",
            (voto.id_candidato_regional,)
        )
        conn.commit()
        return {"message": "Voto regional registrado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/distrital")
async def create_voto_distrital(voto: VotoDistritalCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_VOTANTES FROM VOTANTES WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votante = cursor.fetchone()
        if not votante:
            raise HTTPException(status_code=404, detail="Votante no encontrado")
        cursor.execute("SELECT COUNT(*) FROM VOTO_PRESIDENCIAL WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votos_presidenciales = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTO_REGIONAL WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votos_regionales = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTO_DISTRITAL WHERE ID_VOTANTES = ?", (voto.id_votantes,))
        votos_distritales = cursor.fetchone()[0] or 0
        if votos_presidenciales >= 1 and votos_regionales >= 1 and votos_distritales >= 1:
            raise HTTPException(status_code=400, detail="El votante ya ha ejercido todos sus votos (presidencial, regional y distrital)")
        if votos_distritales >= 1:
            raise HTTPException(status_code=400, detail="El votante ya ha ejercido su voto distrital")
        cursor.execute("SELECT NOMBRES, APELLIDOS FROM CANDIDATO_DISTRITAL WHERE ID_CANDIDATO_DISTRITAL = ?", (voto.id_candidato_distrital,))
        candidato = cursor.fetchone()
        if not candidato:
            raise HTTPException(status_code=404, detail="Candidato distrital no encontrado")
        cursor.execute(
            """INSERT INTO VOTO_DISTRITAL (ID_VOTANTES, ID_CANDIDATO_DISTRITAL, NOMBRE, APELLIDO)
               VALUES (?, ?, ?, ?)""",
            (voto.id_votantes, voto.id_candidato_distrital, candidato[0], candidato[1])
        )
        cursor.execute(
            "UPDATE CANDIDATO_DISTRITAL SET CANTIDAD_VOTOS = CANTIDAD_VOTOS + 1 WHERE ID_CANDIDATO_DISTRITAL = ?",
            (voto.id_candidato_distrital,)
        )
        conn.commit()
        return {"message": "Voto distrital registrado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/nulo")
async def create_voto_nulo(voto: VotoNuloCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO VOTO_NULO (ID_VOTANTES, DNI) VALUES (?, ?)", (voto.id_votantes, voto.dni))
        cursor.execute("UPDATE VOTANTES SET FECHA_VOTO = ? WHERE ID_VOTANTES = ?", (datetime.now(), voto.id_votantes))
        conn.commit()
        return {"message": "Voto nulo registrado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

