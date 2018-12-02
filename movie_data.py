import pandas as pd
from datetime import datetime
from tmdbv3api import TMDb
from tmdbv3api import Movie
from user_dataframe import movies, links, user_movie_matrix
import re

tmdb = TMDb()
tmdb.api_key = 'f773fb6bca4bab1b4a000c4c5e408298'

def sep_year_title(string):
    match = re.match(r'(.*) \((....)\)', string)

    if match == None:
        return ("N/A", "N/A")

    return (match.group(1), match.group(2))

class MovieData:
    def __init__(self, movieId):
        self.movie = movies.loc[(movies['movieId'] == movieId)].max()

        self.title, self.year = sep_year_title(self.movie.title)
        self.id = movieId
        self.genres = self.movie.genres.split('|')
        self.tmdb_id = links.loc[(links['movieId'] == self.id)].max().tmdbId

        try:
            movie = Movie()
            details = movie.details(self.tmdb_id)
            self.title = details.title
            self.poster_url ='http://image.tmdb.org/t/p/w500/' + details.poster_path
            self.overview = details.overview
            self.release_date = details.release_date
            self.runtime = details.runtime
            self.budget = details.budget
            self.revenue = details.revenue
            self.popularity = details.popularity
        except:
            self.poster_url = None
            self.overview = 'Not Found'
            self.release_date = None
            self.runtime = 0
            self.budget = 0
            self.revenue = 0
            self.popularity = 0


    def genres_as_str(self):
        return ', '.join(self.genres)
    
    def budget_as_str(self):
        if self.budget == 0:
            return 'N/A'
        else:
            return "$" + format(self.budget, ",")
    
    def revenue_as_str(self):
        if self.revenue == 0:
            return 'N/A'
        else:
            return "$" + format(self.revenue, ",")
    
    def release_date_as_str(self):
        d = datetime.strptime(self.release_date, '%Y-%m-%d')
        return d.strftime("%B %d, %Y")


def get_random_movie():
    m = movies['movieId'].sample().values
    return MovieData(m[0])