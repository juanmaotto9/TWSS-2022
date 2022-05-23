from bs4 import BeautifulSoup
import requests
import json
import html
import datetime

def jsonMovieTheater(name):
    return {
        '@type': 'MovieTheater',
        'name': name,
    }

def jsonScreeningEvent(name, funcion, format):
    dia = datetime.date.today() + datetime.timedelta(days=1)
    return {
        '@type': 'ScreeningEvent',
        'location': jsonMovieTheater(name),
        'doorTime': f"{dia} {funcion}",
        'videoFormat': format.strip().lower(),
    }

def getMovieFunction(movieSoup):
    horarios = movieSoup.find_all('div', attrs={"class": "col-2"})
    data_function = []
    for horario in horarios:
        cine_sala = horario.find('span').text
        cine_sala = cine_sala.split(" - ")
        funcion = horario.find('p').text

        #reemplazo los saltos de linea con ", " para poder armar mi lista.
        funcion = html.unescape(funcion.replace("\n", ", "))
        funcion = funcion.split(", ")

        #La siguiente linea de codigo elimina los '' que quedan en la lista despues de hacer el replace.
        funcion = list(filter(None, funcion))
        data_function.append(jsonScreeningEvent(cine_sala[0], funcion, cine_sala[1]))
    return data_function

def cinemaLP():
    print("holaaa")
    CinemaLPHTML = requests.get("http://www.cinemalaplata.com/Cartelera.aspx").text
    soup = BeautifulSoup(CinemaLPHTML, "html.parser")
    movies = soup.find_all("div", attrs={"class": "page-container singlepost"})
    movies_data = []
    for movie in movies:
        link = movie.find("a").get("href")
        fullLink = "http://www.cinemalaplata.com/" + link
        movieHTML = requests.get(fullLink).text
        soupmovie = BeautifulSoup(movieHTML, "html.parser")
        movie_name = soupmovie.find("div", attrs={"class": "post-container page-title"}).get_text(strip=True)
        movie_time = getMovieFunction(soupmovie)
        movie_data = {
            "@type": "Movie",
            "name": movie_name,
            "events": movie_time
        }
        movies_data.append(movie_data)


    with open("data/cinemalp.json", "w", encoding='utf8') as outfile:
        outfile.write(json.dumps(movies_data, indent=4, ensure_ascii=False))
    return movies_data


