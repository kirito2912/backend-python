from fastapi import APIRouter, HTTPException
from backend.core.db import get_db_connection
from backend.schemas import VotanteCreate, VotanteStatus
from datetime import datetime

router = APIRouter(prefix="/api/votantes", tags=["votantes"])

@router.post("")
async def create_votante(votante: VotanteCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_VOTANTES FROM VOTANTES WHERE DNI = ?", (votante.dni,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El DNI ya está registrado")
        cursor.execute(
            """INSERT INTO VOTANTES (DNI, NOMBRES, APELLIDOS, FECHA_NACIMIENTO, REGION, DISTRITO)
               OUTPUT INSERTED.ID_VOTANTES VALUES (?, ?, ?, ?, ?, ?)""",
            (votante.dni, votante.nombres, votante.apellidos, votante.fecha_nacimiento, votante.region, votante.distrito)
        )
        id_votantes = cursor.fetchone()[0]
        conn.commit()
        return {"id_votantes": id_votantes, "message": "Votante registrado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/{dni}")
async def get_votante_by_dni(dni: str):
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
            "fecha_voto": str(row[7]) if row[7] else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/{dni}/status", response_model=VotanteStatus)
async def get_votante_status(dni: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_VOTANTES FROM VOTANTES WHERE DNI = ?", (dni,))
        row = cursor.fetchone()
        if not row:
            return VotanteStatus(can_vote_presidencial=True, can_vote_regional=True, can_vote_distrital=True, has_all_votes=False)
        id_votantes = row[0]
        cursor.execute("SELECT COUNT(*) FROM VOTO_PRESIDENCIAL WHERE ID_VOTANTES = ?", (id_votantes,))
        votos_presidenciales = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTO_REGIONAL WHERE ID_VOTANTES = ?", (id_votantes,))
        votos_regionales = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTO_DISTRITAL WHERE ID_VOTANTES = ?", (id_votantes,))
        votos_distritales = cursor.fetchone()[0] or 0
        can_vote_presidencial = votos_presidenciales < 1
        can_vote_regional = votos_regionales < 1
        can_vote_distrital = votos_distritales < 1
        has_all_votes = votos_presidenciales >= 1 and votos_regionales >= 1 and votos_distritales >= 1
        return VotanteStatus(
            can_vote_presidencial=can_vote_presidencial,
            can_vote_regional=can_vote_regional,
            can_vote_distrital=can_vote_distrital,
            has_all_votes=has_all_votes,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("")
async def get_all_votantes(limit: int = 100, offset: int = 0):
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
                "distrito": row[6],
            })
        return votantes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

