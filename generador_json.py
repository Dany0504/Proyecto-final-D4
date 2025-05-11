import csv
import json
import os
from collections import defaultdict

# Ruta base del proyecto
BASE_DIR = r"C:\Users\dany0\Downloads\datos\datos"
CSV_DIR = os.path.join(BASE_DIR, "csv")
CATALOGOS_DIR = os.path.join(CSV_DIR, "catalogos")
JSON_DIR = os.path.join(BASE_DIR, "json")
os.makedirs(JSON_DIR, exist_ok=True)

# Diccionario final de revistas
revistas = defaultdict(lambda: {"areas": [], "catalogos": []})

# Leer revistas desde archivos de área (csv dentro de 'csv')
for archivo in os.listdir(CSV_DIR):
    ruta = os.path.join(CSV_DIR, archivo)

    if not archivo.endswith(".csv") or "catalogos" in archivo.lower():  # Ignorar carpetas de catálogos
        continue

    with open(ruta, encoding="latin-1") as f:
        reader = csv.reader(f)
        for fila in reader:
            if not fila or not fila[0].strip():
                continue
            # El título es la primera columna y el área es el nombre del archivo sin " RadGridExport.csv"
            titulo = fila[0].strip()  
            area = archivo.replace(" RadGridExport.csv", "").strip()  # Aquí se obtiene el área
            if area not in revistas[titulo]["areas"]:
                revistas[titulo]["areas"].append(area)

            # Depuración: Imprimir el título y el área
            print(f"Revista: '{titulo}' | Área: '{area}'")

# Leer revistas desde archivos de catálogo (csv dentro de 'csv/catalogos')
for archivo in os.listdir(CATALOGOS_DIR):
    ruta = os.path.join(CATALOGOS_DIR, archivo)

    if not archivo.endswith(".csv"):
        continue

    # Extraemos solo el nombre del catálogo antes de "_RadGridExport.csv"
    catalogo = archivo.replace("_RadGridExport.csv", "").strip()

    with open(ruta, encoding="latin-1") as f:
        reader = csv.reader(f)
        for fila in reader:
            if not fila or not fila[0].strip():
                continue
            # El título es la primera columna
            titulo = fila[0].strip()  # Sin normalización, manteniendo el título tal cual
            if catalogo not in revistas[titulo]["catalogos"]:
                revistas[titulo]["catalogos"].append(catalogo)

# Guardar resultado como JSON
salida = os.path.join(JSON_DIR, "revistas.json")
with open(salida, "w", encoding="utf-8") as f:
    json.dump(revistas, f, indent=4, ensure_ascii=False)

print(f" JSON generado con éxito en: {salida}")
