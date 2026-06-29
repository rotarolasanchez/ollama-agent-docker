from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import query, reports, health

app = FastAPI(
    title="Facturas AI API",
    description="API para consultar facturas en lenguaje natural usando Ollama + SQL Server",
    version="1.0.0"
)

# CORS — permite que tu app móvil consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: reemplaza con la URL de tu app
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(query.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {"mensaje": "Facturas AI API activa", "docs": "/docs"}
