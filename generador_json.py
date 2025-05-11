import csv
import json
import os
from collections import defaultdict

# Rutas
BASE_DIR = r"C:\Users\dany0\Downloads\datos\datos"
CSV_DIR = os.path.join(BASE_DIR, "csv")
AREAS_DIR = os.path.join(CSV_DIR, "areas")
CATALOGOS_DIR = os.path.join(CSV_DIR, "catalogos")
JSON_DIR = os.path.join(BASE_DIR, "json")
os.makedirs(JSON_DIR, exist_ok=True)

# Diccionario final
revistas = defaultdict(lambda: {"areas": [], "catalogos": []})

# Leer archivos de áreas
for archivo in os.listdir(AREAS_DIR):
    if not archivo.endswith(".csv"):
        continue

    area = archivo.replace(" RadGridExport.csv", "").strip()
    ruta = os.path.join(AREAS_DIR, archivo)

    with open(ruta, encoding="latin-1") as f:
        reader = csv.reader(f)
        next(reader, None)  # Saltar encabezado
        for fila in reader:
            if not fila or not fila[0].strip():
                continue
            titulo = fila[0].strip()
            if area not in revistas[titulo]["areas"]:
                revistas[titulo]["areas"].append(area)

# Leer archivos de catálogos
for archivo in os.listdir(CATALOGOS_DIR):
    if not archivo.endswith(".csv"):
        continue

    catalogo = archivo.replace("_RadGridExport.csv", "").strip()
    ruta = os.path.join(CATALOGOS_DIR, archivo)

    with open(ruta, encoding="latin-1") as f:
        reader = csv.reader(f)
        next(reader, None)
        for fila in reader:
            if not fila or not fila[0].strip():
                continue
            titulo = fila[0].strip()
            if catalogo not in revistas[titulo]["catalogos"]:
                revistas[titulo]["catalogos"].append(catalogo)

# Guardar resultado en JSON
salida = os.path.join(JSON_DIR, "revistas.json")
with open(salida, "w", encoding="utf-8") as f:
    json.dump(revistas, f, indent=4, ensure_ascii=False)

print(f" JSON generado con éxito en: {salida}")
