from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.schemas import ReportResponse
from services.llm_service import generar_reporte, ask_ollama
from services.sql_service import run_query
from db.connection import get_db
from datetime import datetime

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.get("/resumen-mensual", response_model=ReportResponse)
async def resumen_mensual(mes: int = None, anio: int = None, db: Session = Depends(get_db)):
    hoy = datetime.now()
    mes  = mes  or hoy.month
    anio = anio or hoy.year
    sql = f"""
        SELECT COUNT(*) AS total_facturas, SUM(Total_con_Impuesto) AS monto_total,
               SUM(CASE WHEN TerminoPago_Resumen='Contado' THEN Total_con_Impuesto ELSE 0 END) AS contado,
               SUM(CASE WHEN TerminoPago_Resumen='Credito' THEN Total_con_Impuesto ELSE 0 END) AS credito
        FROM VentasCubo
        WHERE Mes_Texto='{hoy.strftime('%B') if not mes else mes}' AND Anio={anio}
        AND Documento='Factura' AND TipoVenta='Venta Neta'
    """
    datos = run_query(db, sql)
    resumen = await generar_reporte("resumen_mensual", datos)
    return ReportResponse(tipo="resumen_mensual", resumen=resumen, datos=datos)

@router.get("/top-proveedores", response_model=ReportResponse)
async def top_clientes(top: int = 5, db: Session = Depends(get_db)):
    sql = f"""
        SELECT TOP {top} Cliente, COUNT(*) AS facturas, SUM(Total_con_Impuesto) AS total_facturado
        FROM VentasCubo
        WHERE Documento='Factura' AND TipoVenta='Venta Neta'
        GROUP BY Cliente ORDER BY total_facturado DESC
    """
    datos = run_query(db, sql)
    resumen = await generar_reporte("top_clientes", datos)
    return ReportResponse(tipo="top_clientes", resumen=resumen, datos=datos)

@router.get("/pendientes", response_model=ReportResponse)
async def facturas_pendientes(db: Session = Depends(get_db)):
    sql = """
        SELECT NumeroLegal, Cliente, FechaEmision, FechaVencimiento,
               Total_con_Impuesto, Moneda
        FROM VentasCubo
        WHERE TerminoPago_Resumen='Credito' AND DiasVencimiento > 0
        ORDER BY FechaVencimiento ASC
    """
    datos = run_query(db, sql)
    resumen = await generar_reporte("facturas_pendientes", datos)
    return ReportResponse(tipo="facturas_pendientes", resumen=resumen, datos=datos)

@router.get("/recomendar/{cliente_id}", response_model=ReportResponse)
async def recomendar_productos(cliente_id: str, db: Session = Depends(get_db)):
    sql_historial = f"""
        SELECT Producto, Categoria, Familia, Marca,
               SUM(Cantidad) AS total_cantidad,
               SUM(Total_con_Impuesto) AS total_comprado
        FROM VentasCubo
        WHERE Cliente_ID = '{cliente_id}'
        AND Documento = 'Factura'
        AND TipoVenta = 'Venta Neta'
        AND FechaEmision >= DATEADD(month, -3, GETDATE())
        GROUP BY Producto, Categoria, Familia, Marca
        ORDER BY total_comprado DESC
    """
    historial = run_query(db, sql_historial)
    if not historial:
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} sin compras en los últimos 3 meses")

    sql_top_otros = f"""
        SELECT TOP 10 Producto, Categoria, Familia, Marca,
               SUM(Cantidad) AS popularidad
        FROM VentasCubo
        WHERE Documento = 'Factura'
        AND TipoVenta = 'Venta Neta'
        AND FechaEmision >= DATEADD(month, -3, GETDATE())
        AND Producto NOT IN (
            SELECT DISTINCT Producto FROM VentasCubo
            WHERE Cliente_ID = '{cliente_id}'
        )
        GROUP BY Producto, Categoria, Familia, Marca
        ORDER BY popularidad DESC
    """
    productos_nuevos = run_query(db, sql_top_otros)

    prompt = f"""Eres un asesor comercial de lubricantes. Analiza el historial de compras de un cliente
y sugiere productos que podría necesitar pero aún no ha comprado.

Historial de compras del cliente (últimos 3 meses):
{historial}

Productos populares que este cliente NO ha comprado:
{productos_nuevos}

Sugiere 3 productos específicos con una razón breve para cada uno.
Responde en español, de forma comercial y directa."""

    recomendacion = await ask_ollama(prompt)
    return ReportResponse(
        tipo="recomendacion",
        resumen=recomendacion,
        datos=productos_nuevos[:3]
    )

@router.get("/cliente-top-recomendacion", response_model=ReportResponse)
async def cliente_top_con_recomendacion(db: Session = Depends(get_db)):
    sql_top = """
        SELECT TOP 1 Cliente_ID, Cliente, SUM(Total_con_Impuesto) AS total
        FROM VentasCubo
        WHERE Documento='Factura' AND TipoVenta='Venta Neta'
        AND FechaEmision >= DATEADD(month, -3, GETDATE())
        GROUP BY Cliente_ID, Cliente
        ORDER BY total DESC
    """
    top = run_query(db, sql_top)
    if not top:
        raise HTTPException(status_code=404, detail="Sin datos en los últimos 3 meses")

    cliente_id  = top[0]["Cliente_ID"]
    cliente_nom = top[0]["Cliente"]

    sql_historial = f"""
        SELECT Producto, Familia, Marca, SUM(Cantidad) AS qty, SUM(Total_con_Impuesto) AS total
        FROM VentasCubo
        WHERE Cliente_ID='{cliente_id}' AND Documento='Factura' AND TipoVenta='Venta Neta'
        AND FechaEmision >= DATEADD(month, -3, GETDATE())
        GROUP BY Producto, Familia, Marca ORDER BY total DESC
    """
    historial = run_query(db, sql_historial)

    sql_nuevos = f"""
        SELECT TOP 5 Producto, Familia, Marca, SUM(Cantidad) AS popularidad
        FROM VentasCubo
        WHERE Documento='Factura' AND TipoVenta='Venta Neta'
        AND FechaEmision >= DATEADD(month, -3, GETDATE())
        AND Producto NOT IN (
            SELECT DISTINCT Producto FROM VentasCubo WHERE Cliente_ID='{cliente_id}'
        )
        GROUP BY Producto, Familia, Marca ORDER BY popularidad DESC
    """
    nuevos = run_query(db, sql_nuevos)

    prompt = f"""Eres un asesor comercial experto en lubricantes Vistony.

Cliente top de los últimos 3 meses: {cliente_nom}
Total comprado: S/ {top[0]['total']:.2f}

Lo que ya compra habitualmente:
{historial}

Productos populares que NO ha comprado:
{nuevos}

En base a su perfil de compras, sugiere 3 productos que debería ofrecerle y por qué.
Sé concreto y comercial. Responde en español."""

    recomendacion = await ask_ollama(prompt)
    return ReportResponse(
        tipo="recomendacion_cliente_top",
        resumen=recomendacion,
        datos=[{"cliente": cliente_nom, "total_3_meses": str(top[0]["total"])}] + nuevos[:3]
    )
