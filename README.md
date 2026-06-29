# ollama-agent-docker

API REST que convierte preguntas en **lenguaje natural** a consultas SQL y devuelve respuestas en español, usando un LLM local con Ollama.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-LLaMA3-black?logo=ollama&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL_Server-2022-CC2927?logo=microsoftsqlserver&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

---

## ¿Qué hace?

El usuario escribe una pregunta en español → el LLM la convierte a T-SQL → se ejecuta contra SQL Server → el LLM resume los resultados en lenguaje natural.

```
Usuario: "¿Cuáles son los 5 productos más vendidos este año?"
    │
    ▼
┌─────────────┐     prompt      ┌─────────────────┐
│   FastAPI   │ ──────────────► │  Ollama (LLaMA) │
│   /query    │ ◄────────────── │  genera T-SQL   │
└─────────────┘     SQL         └─────────────────┘
    │
    ▼ ejecuta
┌─────────────┐
│  SQL Server │  VentasCubo
│  2022       │
└─────────────┘
    │
    ▼ datos
┌─────────────┐     datos       ┌─────────────────┐
│   FastAPI   │ ──────────────► │  Ollama (LLaMA) │
│             │ ◄────────────── │  resume en ES   │
└─────────────┘   respuesta     └─────────────────┘
    │
    ▼
"Los 5 productos más vendidos son: Aceite 10W30 (1,240 und), ..."
```

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| API | FastAPI 0.111 + Python 3.11 |
| LLM | Ollama con LLaMA 3.2 (local, sin API key) |
| Base de datos | SQL Server 2022 Express |
| ORM | SQLAlchemy + pyodbc |
| Contenedores | Docker Compose |

---

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado de todos los servicios |
| `POST` | `/query` | Pregunta en lenguaje natural |
| `GET` | `/reportes/resumen-mensual` | Resumen de ventas del mes actual |
| `GET` | `/reportes/top-proveedores?top=5` | Top N por volumen de ventas |
| `GET` | `/reportes/pendientes` | Documentos pendientes de pago |
| `GET` | `/docs` | Swagger UI interactivo |

---

## Inicio rápido

### Requisitos
- Docker Desktop

### 1. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tu editor y cambiar las contraseñas
```

### 2. Levantar el stack

```bash
docker compose up -d
```

Esto levanta automáticamente:
- SQL Server en el puerto `1433`
- Ollama en el puerto `11434` (descarga el modelo ~2GB la primera vez)
- La API en `http://localhost:8000`

### 3. Verificar

```bash
docker compose ps
curl http://localhost:8000/health
```

### 4. Probar

Abre **http://localhost:8000/docs** para el Swagger interactivo, o usa curl:

```bash
# Consulta en lenguaje natural
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Cuáles son los 5 clientes con más ventas este año?"}'
```

Respuesta:
```json
{
  "pregunta": "¿Cuáles son los 5 clientes con más ventas este año?",
  "sql_generado": "SELECT TOP 5 Cliente, SUM(Total_con_Impuesto) AS Total FROM VentasCubo WHERE Anio=2026 GROUP BY Cliente ORDER BY Total DESC",
  "respuesta": "Los 5 clientes con mayor volumen de ventas en 2026 son: ...",
  "datos": [...]
}
```

---

## Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `SA_PASSWORD` | Contraseña de SQL Server | — |
| `DB_NAME` | Nombre de la base de datos | `FacturasDB` |
| `OLLAMA_MODEL` | Modelo de Ollama a usar | `llama3.2:1b` |
| `SECRET_KEY` | Clave secreta de la aplicación | — |
| `ENVIRONMENT` | Entorno (`development`/`production`) | `development` |

---

## Estructura del proyecto

```
ollama-agent-docker/
├── api/
│   ├── main.py               # Entrada FastAPI
│   ├── routers/
│   │   ├── query.py          # POST /query — lenguaje natural a SQL
│   │   ├── reports.py        # GET /reportes/*
│   │   └── health.py         # GET /health
│   ├── services/
│   │   ├── llm_service.py    # Comunicación con Ollama
│   │   └── sql_service.py    # Ejecución segura de SQL
│   ├── db/
│   │   └── connection.py     # Conexión SQLAlchemy
│   ├── models/
│   │   └── schemas.py        # Schemas Pydantic
│   ├── Dockerfile
│   └── requirements.txt
├── sqlserver/
│   └── init/
│       └── 01_schema.sql     # Schema inicial de la BD
├── import/
│   ├── importar_csv.py       # Script de carga de datos
│   └── CUBO_VENTAS_EJEMPLO.CSV  # Datos de ejemplo (ficticios)
├── docker-compose.yml
└── .env.example
```

---

## Seguridad implementada

- Solo se permiten consultas `SELECT` — el agente bloquea `INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.
- Auto-corrección de SQL: si el LLM genera SQL inválido, el agente lo reenvía a Ollama con el error para que lo corrija.
- Variables sensibles en `.env` (no incluidas en el repositorio).
