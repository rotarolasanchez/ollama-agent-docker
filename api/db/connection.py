from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "1433")
DB_NAME     = os.getenv("DB_NAME", "FacturasDB")
DB_USER     = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

CONNECTION_STRING = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

engine = create_engine(CONNECTION_STRING, echo=False)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        return str(e)
