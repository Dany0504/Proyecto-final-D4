from flask import Flask, render_template, request
import json
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
JSON_AREAS = BASE_DIR / "json" / "revistas_limpio.json"
JSON_SCIMAGO = BASE_DIR / "json" / "revistas_resultados.json"

def cargar_revistas():
    # 1) Carga de áreas y catálogos (JSON_AREAS)
    with open(JSON_AREAS, "r", encoding="utf-8") as f:
        raw_areas = json.load(f)

    base = {}
    # raw_areas puede ser lista o dict
    if isinstance(raw_areas, list):
        for item in raw_areas:
            titulo_original = item.get("titulo", "").strip()
            key = titulo_original.lower()
            base[key] = {
                "titulo": titulo_original,
                "areas": item.get("areas", []),
                "catalogos": item.get("catalogos", [])
            }
    else:  # dict
        for titulo_original, datos in raw_areas.items():
            key = titulo_original.lower()
            base[key] = {
                "titulo": titulo_original,
                "areas": datos.get("areas", []),
                "catalogos": datos.get("catalogos", [])
            }

    # 2) Carga de SCImago (JSON_SCIMAGO)
    with open(JSON_SCIMAGO, "r", encoding="utf-8") as f:
        raw_scimago = json.load(f)

    for item in (raw_scimago if isinstance(raw_scimago, list) else []):
        titulo_original = item.get("titulo", "").strip()
        if not titulo_original:
            continue
        key = titulo_original.lower()
        if key not in base:
            base[key] = {"titulo": titulo_original, "areas": [], "catalogos": []}
        # Actualizamos con datos de SCImago
        base[key].update({
            "url": item.get("url"),
            "widget": item.get("widget"),
            "ultima_visita": item.get("ultima_visita"),
            "h_index": item.get("h_index"),
            "subject_area": item.get("subject_area"),
            "publisher": item.get("publisher"),
            "issn": item.get("issn"),
            "publication_type": item.get("publication_type")
        })

    return base

# Una sola vez
revistas = cargar_revistas()

def obtener_areas():
    áreas = set()
    for datos in revistas.values():
        for a in datos.get("areas", []):
            áreas.add(a)
    return sorted(áreas)

def obtener_catalogos():
    cats = set()
    for datos in revistas.values():
        for c in datos.get("catalogos", []):
            cats.add(c)
    return sorted(cats)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/area')
def area():
    return render_template('area.html', areas=obtener_areas())

@app.route('/area/<nombre>')
def revistas_por_area(nombre):
    filtro = {
        key: datos
        for key, datos in revistas.items()
        if nombre in datos.get("areas", [])
    }
    return render_template('tabla_revistas.html',
                           titulo=f"Área: {nombre}",
                           revistas=filtro)

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html', catalogos=obtener_catalogos())

@app.route('/catalogo/<nombre>')
def revistas_por_catalogo(nombre):
    filtro = {
        key: datos
        for key, datos in revistas.items()
        if nombre in datos.get("catalogos", [])
    }
    return render_template('tabla_revistas.html',
                           titulo=f"Catálogo: {nombre}",
                           revistas=filtro)

@app.route('/explorar')
def explorar():
    letra = request.args.get('letra', '').upper()
    if letra:
        filtro = {
            key: datos
            for key, datos in revistas.items()
            if datos["titulo"].upper().startswith(letra)
        }
    else:
        filtro = {}
    return render_template('explorar.html', letra=letra, revistas=filtro)

@app.route('/busqueda')
def busqueda():
    q = request.args.get("q", "").lower()
    filtro = {
        key: datos
        for key, datos in revistas.items()
        if q in datos["titulo"].lower()
    }
    return render_template('busqueda.html', query=q, revistas=filtro)

@app.route('/revista/<key>')
def detalle_revista(key):
    datos = revistas.get(key)
    if not datos:
        return "Revista no encontrada", 404
    return render_template('detalle_revista.html', titulo=datos["titulo"], datos=datos)

@app.route('/creditos')
def creditos():
    return render_template('creditos.html')

if __name__ == '__main__':
    app.run(debug=True)
