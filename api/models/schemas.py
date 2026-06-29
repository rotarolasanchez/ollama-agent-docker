from pydantic import BaseModel
from typing import Any, Optional

class QueryRequest(BaseModel):
    pregunta: str

class QueryResponse(BaseModel):
    pregunta: str
    sql_generado: str
    respuesta: str
    datos: Optional[list[dict[str, Any]]] = None

class ReportRequest(BaseModel):
    tipo: str
    mes: Optional[int] = None
    anio: Optional[int] = None

class ReportResponse(BaseModel):
    tipo: str
    resumen: str
    datos: list[dict[str, Any]]
