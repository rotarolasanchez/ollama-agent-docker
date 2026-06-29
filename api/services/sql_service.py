from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Any

DB_SCHEMA_CONTEXT = """
Tabla SQL Server: VentasCubo (es la UNICA tabla, no hay otras tablas)

COLUMNAS EXACTAS:
NumeroLegal, FechaEmision, Documento, TipoVenta, Cliente, Cliente_ID, RUC,
Producto, Marca, Categoria, Familia, Vendedor, Supervisor, Gerencia, Zona,
Distrito, Departamento, Total_con_Impuesto, Total_sin_Impuesto, Cantidad,
Galones, Descuento, Moneda, Anio, Mes_Texto, TerminoPago_Resumen

IMPORTANTE SOBRE EL CAMPO Documento:
- Contiene 'Factura' y 'Nota de Credito'
- Las Notas de Credito tienen montos NEGATIVOS y restan al total
- NO filtrar por Documento a menos que el usuario lo pida explicitamente
- Al sumar totales, incluir TODOS los documentos para tener el neto real
- Solo filtrar Documento='Factura' si el usuario dice explicitamente 'solo facturas'

EJEMPLOS DE SQL CORRECTO:
-- Cliente con mas ventas (incluye notas de credito para total neto):
SELECT TOP 1 Cliente, SUM(Total_con_Impuesto) AS Total FROM VentasCubo GROUP BY Cliente ORDER BY SUM(Total_con_Impuesto) DESC

-- Productos mas vendidos:
SELECT TOP 5 Producto, SUM(Cantidad) AS Total FROM VentasCubo GROUP BY Producto ORDER BY Total DESC

-- Ventas por mes:
SELECT Mes_Texto, SUM(Total_con_Impuesto) AS Total FROM VentasCubo WHERE Anio=2026 GROUP BY Mes_Texto ORDER BY Total DESC

-- Factura mas grande:
SELECT TOP 1 NumeroLegal, Cliente, Total_con_Impuesto FROM VentasCubo WHERE Documento='Factura' ORDER BY Total_con_Impuesto DESC

-- Total de registros:
SELECT COUNT(*) AS Total FROM VentasCubo

REGLAS:
- SOLO usar la tabla VentasCubo, NUNCA hacer JOIN con otras tablas
- Usar TOP en lugar de LIMIT
- Sin backticks
- Solo SELECT
- NO filtrar por Documento salvo que el usuario lo pida
"""

def run_query(db: Session, sql: str) -> list[dict[str, Any]]:
    try:
        result = db.execute(text(sql))
        cols = list(result.keys())
        rows = [dict(zip(cols, row)) for row in result.fetchall()]
        return rows
    except Exception as e:
        raise ValueError(f"Error al ejecutar SQL: {e}")

def safe_sql(sql: str) -> str:
    sql_upper = sql.strip().upper()
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "EXEC"]
    for word in forbidden:
        if sql_upper.startswith(word) or f" {word} " in sql_upper:
            raise ValueError(f"Solo se permiten consultas SELECT. Se detecto: {word}")
    return sql
