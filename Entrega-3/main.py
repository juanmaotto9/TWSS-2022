import json
from rdflib import Graph, Literal, RDF, RDFS, URIRef, OWL, Namespace
from rdflib.namespace import FOAF, XSD
from datetime import datetime
from scrapper_cinemaLP import cinemaLP
from scrapper_imdb import getIMDB

BASE_URL = Namespace("http://www.semanticweb.org/")
BASE_SCHEMAORG_URL = Namespace("https://schema.org/")

g = Graph()
g.bind("schema", BASE_SCHEMAORG_URL)
g.bind("sw", BASE_URL)


def position_of(node_type: str, url):
    return len(list(g.triples((None, RDF.type, url[node_type]))))


def add_individual(node_type, label, url=BASE_URL):
    for s, p, o in g.triples((None, RDFS.label, Literal(label))):
        return s

    label = label.replace(":", "")
    individual = BASE_URL[label.replace(" ", "_")]
    g.add((individual, RDF.type, url[node_type]))
    g.add((individual, RDFS.label, Literal(label)))
    g.add((individual, BASE_SCHEMAORG_URL["name"], Literal(label)))
    return individual


def add_actor(movie, actor):
    g.add((movie, BASE_SCHEMAORG_URL["actor"], 
        add_individual(
            actor.get("@type"),
            actor.get("name"),
            url= BASE_SCHEMAORG_URL
        )))


def add_genre(movie, genre):
    g.add((movie, BASE_SCHEMAORG_URL["genre"], Literal(genre)))


def add_director(movie, director):
    g.add((movie, BASE_SCHEMAORG_URL["director"],
           add_individual(
               director.get("@type"),
               director.get("name"),
               url=BASE_SCHEMAORG_URL
           )))

def add_image(an_image):
    image= BASE_URL["image"+str(position_of("ImageObject", url=BASE_SCHEMAORG_URL))]
    g.add((image, RDF.type, BASE_SCHEMAORG_URL["ImageObject"]))
    g.add((image, BASE_SCHEMAORG_URL["contentUrl"], Literal(an_image)))
    return image


def add_movie(a_movie):
    movie_individual = add_individual(
        movie.get("@type"),
        movie.get("name"),
        url=BASE_SCHEMAORG_URL
    )

    g.add((movie_individual, BASE_SCHEMAORG_URL["duration"],
           Literal(movie.get("duration"), datatype=XSD.duration))) if movie.get("duration") else None
    g.add((movie_individual, BASE_SCHEMAORG_URL["image"], add_image(movie.get("image")))) if movie.get(
        "image") else None
    g.add((movie_individual, BASE_SCHEMAORG_URL["datePublished"],
           Literal(datetime.strptime(movie.get("datePublished"), '%Y-%m-%d').isoformat(),
                   datatype=XSD.date))) if movie.get("datePublished") else None

    for actor in movie.get("actor") or []:
        add_actor(movie_individual, actor)
    for genre in movie.get("genre") or []:
        add_genre(movie_individual, genre)
    for director in movie.get("director") or []:
        add_director(movie_individual, director)

def data_in_grafh(a_fuction, a_cinema, function, movie ):
    g.add((a_fuction, RDF.type, BASE_SCHEMAORG_URL["ScreeningEvent"]))
    g.add((a_fuction, BASE_SCHEMAORG_URL["videoFormat"], Literal(function.get("videoFormat"))))
    g.add((a_fuction, BASE_SCHEMAORG_URL["doorTime"], Literal(function.get("doorTime"))))
    g.add((a_fuction, BASE_SCHEMAORG_URL["workPresented"], movie))
    g.add((a_cinema, BASE_SCHEMAORG_URL["location"], a_cinema))

def add_functions(a_movie):
    movie = add_individual("Movie", a_movie.get("name"), BASE_SCHEMAORG_URL)

    for function in a_movie.get("events"):
        function_cine = BASE_URL["screeningEvent" + str(position_of("ScreeningEvent", url=BASE_SCHEMAORG_URL))]

        cine = function.get("location")
        cinema = add_individual(
            cine.get("@type"),
            cine.get("name"),
            url=BASE_SCHEMAORG_URL)

        data_in_grafh(function_cine, cinema, function, movie)


def add_movies(a_movie):

    pelicula = add_individual(
        a_movie.get("@type"),
        a_movie.get("name"),
        url=BASE_SCHEMAORG_URL
    )

    if (a_movie.get("duration") is not None):
        g.add((URIRef(pelicula), BASE_SCHEMAORG_URL["duration"], Literal(a_movie.get("duration"), datatype=XSD.duration)))

    if (a_movie.get("image") is not None):
        g.add((URIRef(pelicula), BASE_SCHEMAORG_URL["image"], add_image(a_movie.get("image"))))

    if (a_movie.get("datePublished") is not None):
        g.add((URIRef(pelicula), BASE_SCHEMAORG_URL["datePublished"], Literal(datetime.strptime(a_movie.get("datePublished"), '%Y-%m-%d').isoformat(), datatype=XSD.date)))

    for actor in a_movie.get("actor") or []:
        add_actor(pelicula, actor)

    for genre in a_movie.get("genre") or []:
        add_genre(pelicula, genre)

    for director in a_movie.get("director") or []:
        add_director(pelicula, director)


if __name__ == '__main__':
    #Recomiendo comentar las llamadas a funciones de otros archivos luego de la primera ejecución del código.
    #getIMDB()
    #cinemaLP()
    with open('data/imdb.json', encoding='utf-8') as fh:
        json_peliculas = json.load(fh)

    with open('data/cinemalp.json', encoding='utf-8') as fh:
        json_cinemaLP = json.load(fh)

    g.parse("data/ontology.ttl", format='ttl', encoding="utf-8")

    for movie in json_peliculas:
        add_movie(movie)

    for movie in json_cinemaLP:
        add_functions(movie)

    g.serialize("data/result_TP3.ttl", format="ttl", encoding="utf-8")


