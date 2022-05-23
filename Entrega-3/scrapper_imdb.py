from bs4 import BeautifulSoup
import requests
import json

def getIMDB():
    jsonMovies = []
    page = requests.get('https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm').text
    soup = BeautifulSoup(page, "html.parser")
    movies = soup.find_all('td', attrs={"class": "titleColumn"})
    movies
    for movie in movies:
        link = movie.find('a').get('href')
        fullLink = "https://www.imdb.com/" + link
        movieHTML= requests.get(fullLink).text
        soupmovie= BeautifulSoup(movieHTML, "html.parser")
        jsonPage = soupmovie.find(
            'script', {'type': 'application/ld+json'}).contents
        json_object = json.loads("".join(jsonPage), strict=False)
        jsonMovies.append(json_object)

    with open("data/imdb.json", "w", encoding='utf8') as outfile:
        outfile.write(json.dumps(jsonMovies, indent=4, ensure_ascii=False))
    return jsonMovies
