from flask import Flask, render_template, request
import pymongo

app = Flask(__name__)

MONGO_URI = "mongodb://localhost:27017/"
cliente = pymongo.MongoClient(MONGO_URI)
db = cliente["noticias_db"]
coleccion = db["noticias"]

NOTICIAS_POR_PAGINA = 20

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    skip = (page - 1) * NOTICIAS_POR_PAGINA

    total_noticias = coleccion.count_documents({"categoria": {"$exists": True}})
    noticias = list(coleccion.find({"categoria": {"$exists": True}})
                               .sort("fecha_publicacion", -1)
                               .skip(skip)
                               .limit(NOTICIAS_POR_PAGINA))

    total_paginas = (total_noticias + NOTICIAS_POR_PAGINA - 1) // NOTICIAS_POR_PAGINA

    return render_template("index.html", noticias=noticias, page=page, total_paginas=total_paginas)

@app.route('/categoria/<categoria>')
def categoria(categoria):
    page = int(request.args.get('page', 1))
    skip = (page - 1) * NOTICIAS_POR_PAGINA

    total_noticias = coleccion.count_documents({"categoria": categoria})
    noticias = list(coleccion.find({"categoria": categoria})
                               .sort("fecha_publicacion", -1)
                               .skip(skip)
                               .limit(NOTICIAS_POR_PAGINA))

    total_paginas = (total_noticias + NOTICIAS_POR_PAGINA - 1) // NOTICIAS_POR_PAGINA

    return render_template("categoria.html", noticias=noticias, categoria=categoria, page=page, total_paginas=total_paginas)

if __name__ == '__main__':
    app.run(debug=True)
