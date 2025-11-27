from fastapi import APIRouter, HTTPException
from backend.core.db import get_db_connection
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/dashboard")
async def get_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        today = datetime.now().date()
        cursor.execute(
            """SELECT COUNT(DISTINCT ID_VOTANTES) FROM VOTANTES WHERE CAST(FECHA_VOTO AS DATE) = ?""",
            (today,)
        )
        active_voters = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTANTES WHERE FECHA_VOTO IS NOT NULL")
        total_votes = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTANTES")
        total_votantes = cursor.fetchone()[0] or 1
        participation_rate = round((total_votes / total_votantes * 100), 2) if total_votantes > 0 else 0
        cursor.execute(
            """SELECT NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_PRESIDENCIAL ORDER BY CANTIDAD_VOTOS DESC"""
        )
        rows = cursor.fetchall()
        top_presidential = []
        for row in rows[:5]:
            votos = row[2] or 0
            pct = (votos / total_votes * 100) if total_votes > 0 else 0
            top_presidential.append({"nombre": f"{row[0]} {row[1]}", "votos": votos, "porcentaje": round(pct, 2)})
        return {
            "metrics": {
                "activeVoters": active_voters,
                "participationRate": participation_rate,
                "totalVotes": total_votes,
            },
            "topPresidential": top_presidential,
            "updatedAt": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/candidates")
async def get_all_candidates():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_CANDIDATO_PRESIDENCIAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_PRESIDENCIAL")
        pres = [
            {"id": r[0], "nombres": r[1], "apellidos": r[2], "nombre_completo": f"{r[1]} {r[2]}", "cantidad_votos": r[3] or 0}
            for r in cursor.fetchall()
        ]
        cursor.execute("SELECT ID_CANDIDATO_REGIONAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_REGIONAL")
        reg = [
            {"id": r[0], "nombres": r[1], "apellidos": r[2], "nombre_completo": f"{r[1]} {r[2]}", "cantidad_votos": r[3] or 0}
            for r in cursor.fetchall()
        ]
        cursor.execute("SELECT ID_CANDIDATO_DISTRITAL, NOMBRES, APELLIDOS, CANTIDAD_VOTOS FROM CANDIDATO_DISTRITAL")
        dist = [
            {"id": r[0], "nombres": r[1], "apellidos": r[2], "nombre_completo": f"{r[1]} {r[2]}", "cantidad_votos": r[3] or 0}
            for r in cursor.fetchall()
        ]
        return {"presidenciales": pres, "regionales": reg, "distritales": dist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/processing-status")
async def get_admin_processing_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM VOTANTES WHERE FECHA_VOTO IS NOT NULL")
        vote_count = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTANTES WHERE FECHA_VOTO IS NULL")
        null_count = cursor.fetchone()[0] or 0
        return {
            "voteCount": vote_count,
            "hasNullData": null_count > 0,
            "nullCount": null_count,
            "updatedAt": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

