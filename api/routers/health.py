from fastapi import APIRouter
from db.connection import test_connection
import httpx, os

router = APIRouter(prefix="/health", tags=["Estado"])
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

@router.get("/")
async def health():
    db_ok = test_connection()
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OLLAMA_HOST}/api/tags")
        ollama_ok = r.status_code == 200
    except Exception:
        ollama_ok = False
    return {
        "api": "ok",
        "base_de_datos": "ok" if db_ok is True else db_ok,
        "ollama": "ok" if ollama_ok else "no disponible"
    }
