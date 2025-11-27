from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import re
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Sistema Electoral API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.routers.auth import router as auth_router
from backend.routers.votantes import router as votantes_router
from backend.routers.candidatos import router as candidatos_router
from backend.routers.votos import router as votos_router
from backend.routers.resultados import router as resultados_router, router_admin as resultados_admin_router
from backend.routers.processing import router as processing_router
from backend.routers.analysis import router as analysis_router
from backend.routers.training import router as training_router

app.include_router(auth_router)
app.include_router(votantes_router)
app.include_router(candidatos_router)
app.include_router(votos_router)
app.include_router(resultados_router)
app.include_router(resultados_admin_router)
app.include_router(processing_router)
app.include_router(analysis_router)
app.include_router(training_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

