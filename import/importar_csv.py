"""
importar_csv.py — carga CUBO_VENTAS_7_3.CSV a SQL Server en Docker
Ejecutar desde PowerShell:
    pip install pandas pyodbc sqlalchemy
    python importar_csv.py
"""

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import os

# ── CONFIGURACIÓN ─────────────────────────────────────────────
CSV_FILE   = "CUBO_VENTAS_7_3.CSV"   # pon el CSV en la misma carpeta que este script
SA_PASSWORD = input("Ingresa tu SA_PASSWORD de SQL Server: ")

CONNECTION = (
    f"mssql+pyodbc://sa:{SA_PASSWORD}@localhost:1433/FacturasDB"
    "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

# ── COLUMNAS A IMPORTAR (las que existen en la tabla) ────────
COLUMNAS = {
    "Documento_ID":         "Documento_ID",
    "NumeroLegal":          "NumeroLegal",
    "NumInternoFact":       "NumInternoFact",
    "FechaEmision":         "FechaEmision",
    "FechaVencimiento":     "FechaVencimiento",
    "DiasVencimiento":      "DiasVencimiento",
    "Anio":                 "Anio",
    "Mes_Texto":            "Mes_Texto",
    "Dia_Num":              "Dia_Num",
    "Documento":            "Documento",
    "TipoVenta":            "TipoVenta",
    "TerminoPago":          "TerminoPago",
    "TerminoPago_Resumen":  "TerminoPago_Resumen",
    "CondicionPago":        "CondicionPago",
    "Indicador_Impuesto":   "Indicador_Impuesto",
    "Moneda":               "Moneda",
    "Tipo_Cambio":          "Tipo_Cambio",
    "Almacen":              "Almacen",
    "Cliente_ID":           "Cliente_ID",
    "Domicilio_ID":         "Domicilio_ID",
    "Cliente":              "Cliente",
    "RUC":                  "RUC",
    "TipoIdentificacion":   "TipoIdentificacion",
    "Cliente_Categoria":    "Cliente_Categoria",
    "CategoriaPotencial":   "CategoriaPotencial",
    "Giro_Negocio":         "Giro_Negocio",
    "Actividad":            "Actividad",
    "Linea_Credito":        "Linea_Credito",
    "Correo":               "Correo",
    "Telefono_1":           "Telefono",
    "Dia_Ruta":             "Dia_Ruta",
    "Dias_Entrega":         "Dias_Entrega",
    "Domicilio":            "Domicilio",
    "Distrito":             "Distrito",
    "Provincia":            "Provincia",
    "Departamento":         "Departamento",
    "Pais":                 "Pais",
    "Ubigeo":               "Ubigeo",
    "Zona_ID":              "Zona_ID",
    "Zona":                 "Zona",
    "Producto_ID":          "Producto_ID",
    "Producto":             "Producto",
    "CodigoBarra":          "CodigoBarra",
    "UnidadMedida":         "UnidadMedida",
    "Tecnologia":           "Tecnologia",
    "Categoria":            "Categoria",
    "Categoria_ID":         "Categoria_ID",
    "Familia":              "Familia",
    "Familia_ID":           "Familia_ID",
    "SubFamilia":           "SubFamilia",
    "SubFamilia_ID":        "SubFamilia_ID",
    "Linea":                "Linea",
    "Linea_ID":             "Linea_ID",
    "Marca":                "Marca",
    "GrupoProducto":        "GrupoProducto",
    "Subcanal":             "Subcanal",
    "DIM_VENDEDOR_Vendedor_ID": "Vendedor_ID",
    "Vendedor":             "Vendedor",
    "Analista":             "Analista",
    "Supervisor":           "Supervisor",
    "Gerencia":             "Gerencia",
    "UnidadNegocio":        "UnidadNegocio",
    "GrupoUnidadNegocio":   "GrupoUnidadNegocio",
    "Sectorista":           "Sectorista",
    "TipoGerencia":         "TipoGerencia",
    "TipoGerencia_ID":      "TipoGerencia_ID",
    "CentroCosto":          "CentroCosto",
    "LineaProduccion":      "LineaProduccion",
    "Procedencia":          "Procedencia",
    "PromID":               "PromID",
    "FISE":                 "FISE",
    "Motivo_Descuento":     "Motivo_Descuento",
    "Precio":               "Precio",
    "PrecioAntesDscto":     "PrecioAntesDscto",
    "Total_con_Impuesto":   "Total_con_Impuesto",
    "Total_sin_Impuesto":   "Total_sin_Impuesto",
    "Total_Costo":          "Total_Costo",
    "Cantidad":             "Cantidad",
    "Galones":              "Galones",
    "Descuento":            "Descuento",
    "Descuento_2":          "Descuento_2",
    "Descuento_Porc":       "Descuento_Porc",
    "DescuentoFinanciero":  "DescuentoFinanciero",
    "Otros_Descuentos":     "Otros_Descuentos",
    "Total_Promocion":      "Total_Promocion",
    "Cuenta":               "Cuenta",
    "Sucursal":             "Sucursal",
}

def limpiar_fecha(val):
    if pd.isna(val) or str(val).strip() in ["", "?"]:
        return None
    try:
        return pd.to_datetime(str(val).strip(), format="%b %d, %Y").date()
    except:
        return None

def limpiar_decimal(val):
    if pd.isna(val) or str(val).strip() in ["", "?"]:
        return None
    try:
        return float(str(val).replace(",", "").strip())
    except:
        return None

print(f"\n>>> Leyendo {CSV_FILE}...")
df = pd.read_csv(CSV_FILE, sep=";", encoding="latin-1", dtype=str, skiprows=0)
df.columns = df.columns.str.strip()
df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

print(f"    {len(df)} filas, {len(df.columns)} columnas detectadas")

# Renombrar columnas según el mapa
cols_disponibles = {k: v for k, v in COLUMNAS.items() if k in df.columns}
df = df[list(cols_disponibles.keys())].rename(columns=cols_disponibles)

# Limpiar fechas
for col in ["FechaEmision", "FechaVencimiento", "FechaCreacionCliente"]:
    if col in df.columns:
        df[col] = df[col].apply(limpiar_fecha)

# Limpiar decimales
decimales = ["Tipo_Cambio","Precio","PrecioAntesDscto","Total_con_Impuesto",
             "Total_sin_Impuesto","Total_Costo","Cantidad","Galones","Descuento",
             "Descuento_2","Descuento_Porc","DescuentoFinanciero","Otros_Descuentos",
             "Total_Promocion","Linea_Credito","DiasVencimiento","Dias_Entrega",
             "Vendedor_ID","TipoGerencia_ID","Anio","Dia_Num"]
for col in decimales:
    if col in df.columns:
        df[col] = df[col].apply(limpiar_decimal)

print(f"\n>>> Conectando a SQL Server...")
engine = create_engine(CONNECTION)

with engine.connect() as conn:
    conn.execute(text("DELETE FROM VentasCubo"))
    conn.commit()
    print("    Tabla limpiada")

print(f">>> Importando {len(df)} registros...")
df.to_sql("VentasCubo", engine, if_exists="append", index=False, chunksize=500)

with engine.connect() as conn:
    total = conn.execute(text("SELECT COUNT(*) FROM VentasCubo")).scalar()

print(f"\n✓ Importación completa: {total} registros en VentasCubo")
