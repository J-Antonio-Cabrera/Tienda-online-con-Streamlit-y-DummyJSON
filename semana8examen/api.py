
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="API del Dólar USD/MXN",
    description="Historial del precio del dólar en pesos mexicanos.",
    version="1.0.0"
)

# Localizar el archivo JSON junto a api.py
RUTA_DATOS = Path(__file__).parent / "dolar_historico.json"

with open(RUTA_DATOS, "r", encoding="utf-8") as archivo:
    datos = json.load(archivo)

dolar = datos["Dolar"]


# Función agregada siguiendo la estructura del maestro
def data_dolar():
    return {"data": dolar}


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a la API del dólar USD/MXN",
        "documentacion": "/docs",
        "total_registros": len(dolar)
    }


@app.get("/dolar")
def obtener_historial():
    return dolar


# Estructura del maestro adaptada al dólar
@app.get("/dolar/{fecha}")
def consultar_fecha(fecha: str):
    dolar = data_dolar()["data"]

    for registro in dolar:
        if registro["fecha"] == fecha:
            return registro

    return {"error": "Dollar price not found"}
