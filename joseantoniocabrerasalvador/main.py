
import json

# 1. Cargar los datos históricos
with open("dolar_historico.json", "r", encoding="utf-8") as archivo:
    datos = json.load(archivo)

dolar = datos["Dolar"]


# 2. Mostrar el historial completo
def mostrar_historial():
    print("\n========== HISTORIAL DEL DÓLAR USD/MXN ==========")

    for registro in dolar:
        print(
            f"Fecha: {registro['fecha']} | "
            f"Precio: ${registro['precio']:.4f} MXN"
        )

    print(f"\nTotal de registros: {len(dolar)}")


# 3. Consultar el precio por fecha
def consultar_fecha():
    fecha = input("\nIngresa la fecha (DD-MM-AAAA): ").strip()

    for registro in dolar:
        if registro["fecha"] == fecha:
            print(
                f"\nFecha consultada: {registro['fecha']}"
                f"\nPrecio del dólar: ${registro['precio']:.4f} MXN"
            )
            return

    print("No se encontró esa fecha en el historial.")


# 4. Menú principal
while True:
    print("\n========== MENÚ PRINCIPAL ==========")
    print("1. Mostrar historial completo")
    print("2. Consultar precio por fecha")
    print("3. Salir")

    opcion = input("Selecciona una opción: ").strip()

    if opcion == "1":
        mostrar_historial()

    elif opcion == "2":
        consultar_fecha()

    elif opcion == "3":
        print("Programa finalizado.")
        break

    else:
        print("Opción no válida. Intenta nuevamente.")
