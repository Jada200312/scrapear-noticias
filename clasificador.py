import google.generativeai as genai # Importar la librería de Gemini
import os
import pymongo


os.environ["GOOGLE_API_KEY"] = "AIzaSyDCb5WLImHqnswqmrvD-bEGed_f8sVIz-k"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")


MONGO_URI = "mongodb://localhost:27017/"  
cliente = pymongo.MongoClient(MONGO_URI)
db = cliente["noticias_db"] 
coleccion = db["noticias"]  


def clasificar_noticia(titulo):
    prompt = f"Clasifica la siguiente noticia en una de estas categorías: Política, Economía, Deportes, Tecnología, Opinión. Noticia: '{titulo}'. Solo responde con el nombre de la categoría."
    respuesta = model.generate_content(prompt)
    return respuesta.text.strip()


def procesar_noticias():
    noticias_sin_clasificar = coleccion.find({"categoria": {"$exists": False}})  

    for noticia in noticias_sin_clasificar:
        categoria = clasificar_noticia(noticia["titulo"])
        coleccion.update_one(
            {"_id": noticia["_id"]},
            {"$set": {"categoria": categoria}}  
        )
        print(f"✅ Noticia clasificada: {noticia['titulo']} → {categoria}")


procesar_noticias()
