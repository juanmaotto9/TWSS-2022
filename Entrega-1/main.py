import bs4
import requests
import json

#Estos los estoy utilizando para cinepolis
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


#http://www.cinemalaplata.com
#https://www.cinepolis.com.ar

def cinemaLP():
    CinemaLPHTML = requests.get("http://www.cinemalaplata.com/Cartelera.aspx").text
    soup = bs4.BeautifulSoup(CinemaLPHTML, "html.parser")
    movies = soup.find_all("div", attrs={"class": "page-container singlepost"})
    movie_dict = {}
    for movie in movies:
        info_arr = []
        link = movie.find("a").get("href")
        fullLink = "http://www.cinemalaplata.com/" + link
        movieHTML = requests.get(fullLink).text
        soupmovie = bs4.BeautifulSoup(movieHTML, "html.parser")
        movie_name = soupmovie.find("div", attrs={"class": "post-container page-title"}).get_text(strip=True)


        cines = soupmovie.find_all("a", attrs={"class": "cine"})
        cines_nombre = []
        for cine in cines:
            cines_nombre.append(cine.string)
        dict_cines = {"cine/s": cines_nombre }
        info_arr.append(dict_cines)

        movieData = soupmovie.find_all("div", attrs={"class": "dropcap6"})
        for data in movieData:
            titulo = data.find("h4").get_text(strip=True)
            dato_real = data.find("span").get_text(strip=True)
            pares = {}
            pares[titulo] = dato_real
            info_arr.append(pares)
        movie_dict[movie_name] = info_arr
    return(movie_dict)


if __name__ == '__main__':
    with open("data/cinemalaplata.json", "w", encoding='utf8') as outfile:
        outfile.write(json.dumps(cinemaLP(), indent=4, ensure_ascii=False))

