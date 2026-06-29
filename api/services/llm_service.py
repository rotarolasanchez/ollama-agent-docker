import httpx
import os
import re
from services.sql_service import DB_SCHEMA_CONTEXT

OLLAMA_HOST  = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

def limpiar_sql(sql: str) -> str:
    sql = re.sub(r"`sql|`|", "", sql).strip()
    sql = re.sub(r'\bLIMIT\s+(\d+)', r'', sql).strip()
    sql = re.sub(r'SELECT\s+(?!TOP\s)', 'SELECT TOP 10 ', sql, count=1)
    return sql

async def ask_ollama(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=600.0) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json()["response"].strip()

async def pregunta_a_sql(pregunta: str) -> str:
    prompt = f"""Eres un experto en SQL Server T-SQL. Convierte la pregunta a SQL valido.

{DB_SCHEMA_CONTEXT}

REGLAS:
- Solo SELECT, nunca INSERT/UPDATE/DELETE/DROP
- Usa TOP en lugar de LIMIT
- Sin backticks, solo comillas simples
- Tabla: VentasCubo
- Fechas: 'YYYY-MM-DD'
- Responde SOLO con el SQL, sin explicaciones

Pregunta: {pregunta}
SQL:"""
    sql = await ask_ollama(prompt)
    return limpiar_sql(sql)

async def datos_a_resumen(pregunta: str, datos: list[dict]) -> str:
    prompt = f"""Eres un asistente de ventas. Responde en espanol claro y conciso.

Pregunta: {pregunta}
Datos: {datos}

Da una respuesta natural y util basada en los datos."""
    return await ask_ollama(prompt)

async def generar_reporte(tipo: str, datos: list[dict]) -> str:
    prompt = f"""Analista de ventas. Resume en 2-3 oraciones en espanol.

Reporte: {tipo}
Datos: {datos}"""
    return await ask_ollama(prompt)
