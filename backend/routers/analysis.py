from fastapi import APIRouter, HTTPException
from backend.core.db import get_db_connection
from datetime import datetime

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.get("/stats")
async def get_analysis_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        today = datetime.now().date()
        cursor.execute(
            """SELECT COUNT(DISTINCT ID_VOTANTES) 
               FROM VOTANTES 
               WHERE CAST(FECHA_VOTO AS DATE) = ?""",
            (today,)
        )
        active_voters = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTANTES WHERE FECHA_VOTO IS NOT NULL")
        total_votes = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM VOTANTES")
        total_votantes = cursor.fetchone()[0] or 1
        participation_rate = round((total_votes / total_votantes * 100), 2) if total_votantes > 0 else 0
        peak_activity_time = "14:30"
        return {"activeVoters": active_voters, "participationRate": participation_rate, "peakActivityTime": peak_activity_time, "totalVotes": total_votes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/voting-flow")
async def get_voting_flow():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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
            flow_data.append({"hour": hour, "votes": row[1]})
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
                {"hour": "17:00", "votes": 0},
            ]
        return flow_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

