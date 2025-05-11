from flask import Flask, render_template, request
import json
import os
from pathlib import Path

app = Flask(__name__)

# Configuración de rutas confiables
BASE_DIR = Path(__file__).parent
JSON_PATH = BASE_DIR / "json" / "revistas_limpio.json"  

# Carga del JSON con verificación
try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        revistas = json.load(f)
except FileNotFoundError:
    print(f"¡Error! No se encontró el archivo JSON en: {JSON_PATH}")
    print("Archivos disponibles en json/:")
    print(os.listdir(BASE_DIR / "json"))
    revistas = {}  # Diccionario vacío para evitar errores

def obtener_areas():
    areas = set()
    for rev in revistas.values():
        for area in rev.get("areas", []):
            areas.add(area)
    return sorted(areas)

def obtener_catalogos():
    cats = set()
    for rev in revistas.values():
        for cat in rev.get("catalogos", []):
            cats.add(cat)
    return sorted(cats)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/area')
def area():
    areas = obtener_areas()
    return render_template('area.html', areas=areas)

@app.route('/area/<nombre>')
def revistas_por_area(nombre):
    filtro = {titulo: data for titulo, data in revistas.items() if nombre in data.get("areas", [])}
    return render_template('tabla_revistas.html', titulo=f"Área: {nombre}", revistas=filtro)

@app.route('/catalogo')
def catalogo():
    catalogos = obtener_catalogos()
    return render_template('catalogo.html', catalogos=catalogos)

@app.route('/catalogo/<nombre>')
def revistas_por_catalogo(nombre):
    filtro = {titulo: data for titulo, data in revistas.items() if nombre in data.get("catalogos", [])}
    return render_template('tabla_revistas.html', titulo=f"Catálogo: {nombre}", revistas=filtro)

@app.route('/explorar')
def explorar():
    letra = request.args.get('letra', '').upper()
    filtro = {titulo: data for titulo, data in revistas.items() if titulo.upper().startswith(letra)} if letra else {}
    return render_template('explorar.html', letra=letra, revistas=filtro)

@app.route('/busqueda')
def busqueda():
    q = request.args.get("q", "").lower()
    filtro = {titulo: data for titulo, data in revistas.items() if q in titulo.lower()}
    return render_template('busqueda.html', query=q, revistas=filtro)

@app.route('/revista/<titulo>')
def detalle_revista(titulo):
    datos = revistas.get(titulo)
    if not datos:
        return "Revista no encontrada", 404
    return render_template('detalle_revista.html', titulo=titulo, datos=datos)

@app.route('/creditos')
def creditos():
    return render_template('creditos.html')

if __name__ == '__main__':
    app.run(debug=True)