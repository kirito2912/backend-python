from fastapi import APIRouter, HTTPException
from backend.core.db import get_db_connection
from datetime import datetime

router = APIRouter(prefix="/api/processing", tags=["processing"])

@router.post("/analyze-quality")
async def analyze_quality():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM VOTANTES")
        total_records = cursor.fetchone()[0] or 0
        cursor.execute(
            """SELECT 
                SUM(CASE WHEN DNI IS NULL THEN 1 ELSE 0 END) as dni_nulls,
                SUM(CASE WHEN NOMBRES IS NULL THEN 1 ELSE 0 END) as nombres_nulls,
                SUM(CASE WHEN FECHA_NACIMIENTO IS NULL THEN 1 ELSE 0 END) as fecha_nulls
               FROM VOTANTES"""
        )
        nulls = cursor.fetchone()
        cursor.execute(
            """SELECT COUNT(*) - COUNT(DISTINCT DNI) as duplicates
               FROM VOTANTES WHERE DNI IS NOT NULL"""
        )
        duplicates = cursor.fetchone()[0] or 0
        return {
            "totalRecords": total_records,
            "nullCounts": {"dni": nulls[0] or 0, "nombres": nulls[1] or 0, "fecha_nacimiento": nulls[2] or 0},
            "duplicateCount": duplicates,
            "dataTypes": {"dni": "varchar", "nombres": "varchar", "fecha_nacimiento": "date"},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/status")
async def get_processing_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM VOTANTES WHERE FECHA_VOTO IS NOT NULL")
        vote_count = cursor.fetchone()[0] or 0
        has_na_data = False
        return {"voteCount": vote_count, "hasNAData": has_na_data, "lastProcessed": datetime.now().isoformat(), "processingHistory": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

