import pandas as pd
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
	def __init__(self, exact_title):
		self.movie = movies.loc[(movies['title'] == exact_title)].max()

		self.title, self.year = sep_year_title(self.movie.title)
		self.id = self.movie.movieId
		self.genres = self.movie.genres

		self.tmdb_id = links.loc[(links['movieId'] == self.id)].max().tmdbId

		movie = Movie()
		details = movie.details(self.tmdb_id)
		self.title = details.title
		self.poster_url ='http://image.tmdb.org/t/p/w500/' + details.poster_path
		self.overview = details.overview
		self.release_date = details.release_date
		self.budget = details.budget
		self.revenue = details.revenue
		self.popularity = details.popularity

		"""
		self.poster_url = 'http://image.tmdb.org/t/p/w500/hCPXcQn1FTYF9AUCPd6o3miM9WX.jpg'
		self.overview = 'TEST'
		self.release_date = 'XX/XX/XXXX'
		self.budget = 1234
		self.revenue = 456
		self.popularity = 789
		"""

	def genres_as_str(self):
		return self.genres

def get_random_movie():
	m = movies['title'].sample().values
	return MovieData(m[0])

#MovieData('Mad Max (1979)')