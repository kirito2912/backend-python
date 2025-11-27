from fastapi import APIRouter, HTTPException
from backend.core.db import get_db_connection

router = APIRouter(prefix="/api/training", tags=["training"])

@router.get("/stats")
async def get_training_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT COUNT(*) 
               FROM VOTANTES 
               WHERE FECHA_VOTO IS NOT NULL"""
        )
        valid_votes = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(DISTINCT ID_CANDIDATO) FROM VOTO_PRESIDENCIAL")
        presidencial_candidates = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(DISTINCT ID_CANDIDATO_REGIONAL) FROM VOTO_REGIONAL")
        regional_candidates = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(DISTINCT ID_CANDIDATO_DISTRITAL) FROM VOTO_DISTRITAL")
        distrital_candidates = cursor.fetchone()[0] or 0
        candidates = presidencial_candidates + regional_candidates + distrital_candidates
        return {"validVotes": valid_votes, "candidates": candidates, "features": ["Edad", "Educación", "Género"], "canTrain": valid_votes >= 10}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

