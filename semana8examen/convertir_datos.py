
import json
from datetime import datetime

# 1. Leer los datos originales
with open("datos_originales.json", "r", encoding="utf-8") as archivo:
    registros = json.load(archivo)

# 2. Convertir los datos al formato solicitado
datos_convertidos = {
    "Dolar": [
        {
            "fecha": datetime.strptime(
                registro["date"], "%Y-%m-%d"
            ).strftime("%d-%m-%Y"),
            "precio": registro["rate"]
        }
        for registro in registros
    ]
}

# 3. Guardar los datos convertidos
with open("dolar_historico.json", "w", encoding="utf-8") as archivo:
    json.dump(
        datos_convertidos,
        archivo,
        ensure_ascii=False,
        indent=4
    )

# 4. Mostrar el resultado
print("Conversión completada correctamente.")
print("Total de registros:", len(datos_convertidos["Dolar"]))
print("Archivo creado: dolar_historico.json")
