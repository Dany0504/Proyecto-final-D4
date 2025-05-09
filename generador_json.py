import csv
import json
import os
from collections import defaultdict

# Ruta base del proyecto
BASE_DIR = r"C:\Users\dany0\Downloads\datos\datos"

# Directorios de entrada
AREAS_DIR = os.path.join(BASE_DIR, "csv", "areas")
CATALOGOS_DIR = os.path.join(BASE_DIR, "csv", "catalogos")

# Directorio de salida
JSON_DIR = os.path.join(BASE_DIR, "json")
os.makedirs(JSON_DIR, exist_ok=True)

# Diccionario para guardar datos
revistas = defaultdict(lambda: {"areas": [], "catalogos": []})

# Leer archivos del directorio de áreas
for archivo in os.listdir(AREAS_DIR):
    if archivo.endswith(".csv"):
        with open(os.path.join(AREAS_DIR, archivo), encoding='latin-1') as f:
            reader = csv.reader(f)
            next(reader)  # Saltar encabezado
            for fila in reader:
                if len(fila) <2:
                    continue
                titulo = fila[0].strip().lower()
                area = fila[1].strip().upper()
                if area not in revistas[titulo]["areas"]:
                    revistas[titulo]["areas"].append(area)

# Leer archivos del directorio de catálogos
for archivo in os.listdir(CATALOGOS_DIR):
    if archivo.endswith(".csv"):
        with open(os.path.join(CATALOGOS_DIR, archivo), encoding='latin-1') as f:
            reader = csv.reader(f)
            next(reader)  # Saltar encabezado
            for fila in reader:
                if len(fila) <2:
                    continue
                titulo = fila[0].strip().lower()
                catalogo = fila[1].strip().upper()
                if catalogo not in revistas[titulo]["catalogos"]:
                    revistas[titulo]["catalogos"].append(catalogo)

# Guardar como JSON
salida_path = os.path.join(JSON_DIR, "revistas.json")
with open(salida_path, "w", encoding="latin-1") as f:
    json.dump(revistas, f, indent=4, ensure_ascii=False)

print(f"Archivo JSON generado en: {salida_path}")