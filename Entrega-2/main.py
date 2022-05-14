import json
from bs4 import BeautifulSoup
import requests

def obtener_info():
    arr_urls = ["https://www.rottentomatoes.com/m/the_batman",
                 "https://www.imdb.com/title/tt1877830/?ref_=fn_al_tt_1",
                 "https://www.ecartelera.com/peliculas/the-batman/"]
    # "https://www.metacritic.com/movie/the-batman", #falta hacer andar este
    info_websites = []
    for url in arr_urls:
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        info = soup.find("script", {"type": "application/ld+json"}).contents
        info_websites.append(json.loads("".join(info), strict=False))

    with open("data/info_websites.json", "w", encoding='utf8') as outfile:
        outfile.write(json.dumps(info_websites, indent=4, ensure_ascii=False))
    return (info_websites)  #retorno un arreglo con la info de los sitios


def obtener_actores(website, actores):
    actores_schema = []
    if "actor" in website:
        actores_schema.extend(website["actor"])
    elif "actors" in website:
        actores_schema.extend(website["actors"])
    for actor in actores_schema:
        if actor["name"] != "NA":
            actores.append(actor["name"])


def obtener_director(website, director):
    director_schema = []
    if "director" in website:
        director_schema.extend(website["director"])
    elif "author" in website:
        director_schema.extend(website["author"])
    for d in director_schema:
        if d["name"] != "NA":
            director.append(d["name"])

def serialize_set(my_list):
    #Este metodo toma la lista que recibe, la convierte en set(eliminar duplicados) y..
    #.. la vuelve a convertir en lista.
    #Este metodo soluciona un error que tira JSON que le impide serializar correctamente un set.
    return(list(set(my_list)))


def merge_info(websites):
    nombre, generos, actores, director, descripciones, duraciones = ([] for i in range(6))
    for website in websites:
        nombre.append(website["name"])
        generos.extend(website["genre"])
        obtener_actores(website, actores)
        obtener_director(website, director)
        if "duration" in website:
            duraciones.append(website["duration"])
        if "description" in website:
            descripciones.append(website["description"])

    merge_final = {
        "@context": "http://schema.org",
        "@type": "Movie",
        "name": serialize_set(nombre),
        "genre": serialize_set(generos),
        "director": serialize_set(director),
        "actor": serialize_set(actores),
        "duration": serialize_set(duraciones),
        "description": descripciones
    }

    with open("data/merge_websites.json", "w", encoding='utf8') as outfile:
        outfile.write(json.dumps(merge_final, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    merge_info(obtener_info())
