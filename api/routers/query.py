from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.schemas import QueryRequest, QueryResponse
from services.llm_service import pregunta_a_sql, datos_a_resumen, ask_ollama
from services.sql_service import run_query, safe_sql, DB_SCHEMA_CONTEXT
from db.connection import get_db
import re

router = APIRouter(prefix="/query", tags=["Consultas"])

async def corregir_sql(sql: str, error: str) -> str:
    prompt = f"""El siguiente SQL de SQL Server es incorrecto:

{sql}

Error recibido: {error}

Corrige el SQL. Responde UNICAMENTE con el SQL corregido, sin explicaciones.
Recuerda: columnas en SELECT que no sean agregadas deben estar en GROUP BY.

SQL corregido:"""
    sql_corregido = await ask_ollama(prompt)
    return re.sub(r"`sql|`", "", sql_corregido).strip()

@router.post("/", response_model=QueryResponse)
async def consulta_natural(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        sql = await pregunta_a_sql(request.pregunta)
        sql = safe_sql(sql)

        # Intenta ejecutar, si falla deja al LLM corregir
        try:
            datos = run_query(db, sql)
        except ValueError as e:
            sql = await corregir_sql(sql, str(e))
            sql = safe_sql(sql)
            datos = run_query(db, sql)

        respuesta = await datos_a_resumen(request.pregunta, datos)
        return QueryResponse(
            pregunta=request.pregunta,
            sql_generado=sql,
            respuesta=respuesta,
            datos=datos
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")
