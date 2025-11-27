from fastapi import APIRouter, HTTPException
from backend.core.db import get_db_connection
from datetime import datetime

router = APIRouter(prefix="/api/resultados", tags=["resultados"])
router_admin = APIRouter(prefix="/api/results", tags=["results"])

@router.get("/presidencial")
async def get_resultados_presidencial():
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
            resultados.append({"id": row[0], "nombre": f"{row[1]} {row[2]}", "votos": votos, "porcentaje": round(porcentaje, 2)})
        return {"total_votos": total_votos, "candidatos": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/regional")
async def get_resultados_regional():
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
            resultados.append({"id": row[0], "nombre": f"{row[1]} {row[2]}", "votos": row[3] or 0})
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/distrital")
async def get_resultados_distrital():
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
            resultados.append({"id": row[0], "nombre": f"{row[1]} {row[2]}", "votos": row[3] or 0})
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router_admin.get("/status")
async def get_results_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT COUNT(*) FROM VOTANTES 
               WHERE FECHA_VOTO IS NULL""")
        null_count = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTANTES WHERE FECHA_VOTO IS NOT NULL")
        total_votes = cursor.fetchone()[0] or 0
        return {"hasNullData": null_count > 0, "nullCount": null_count, "naCount": 0, "totalVotes": total_votes, "lastUpdated": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router_admin.get("/summary")
async def get_results_summary():
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
            candidates.append({"id": row[0], "name": f"{row[1]} {row[2]}", "votes": votes, "percentage": round(percentage, 2)})
        cursor.execute("SELECT COUNT(*) FROM VOTANTES")
        total_votantes = cursor.fetchone()[0] or 1
        participation_rate = round((total_votes / total_votantes * 100), 2) if total_votantes > 0 else 0
        return {"totalVotes": total_votes, "candidates": candidates, "participationRate": participation_rate}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

