import kivy
import gui_helpers as h
from movie_data import MovieData, sep_year_title
from autocomplete import DropDownWidget
from kivy.app import App

from kivy.loader import Loader
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from user_dataframe import movies
from loading_wheel import Loading
from user_dataframe import user_movie_matrix
import pandas as pd
import svd
import difflib

Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '1000')

wrap_info = ("""
Label:
	size_hint: 1, None
	text_size: self.width, None
	height: self.texture_size[1]
	valign: 'top'
""")

wrap_label = ("""
Label:
	size_hint: 1, 0.3
	text_size: self.width, None
	valign: 'top'
	halign: 'right'
""")


data_label = ("""
Label:
	text_size: self.size
	halign: 'right'
	valign: 'top'
	size_hint_y: 1
	size_hint_x: 0.3
""")

data_info = ("""
Label:
	text_size: self.size
	halign: 'left'
	valign: 'top'
""")

self_id = user_movie_matrix.index.values[-1] + 1

class Input(TextInput):
	def __init__(self, movie_window):
		super().__init__()

		self.movie_window = movie_window

	def insert_text(self, substring, from_undo=False):
		text = self.text + substring

		if substring == "\n":
			titles = difflib.get_close_matches(text, movies.title, n=10, cutoff=0.4)
			# check if titles is empty
			if titles:
				if sep_year_title(titles[0]) == ("N/A", "N/A"): # if there isn't a year in the title, quit
					return super(Input, self).insert_text("", from_undo=from_undo)

				movie_data = MovieData(titles[0])
				self.text = titles[0]
				self.movie_window.mpi.update(movie_data)
				self.movie_window.current_movie = movie_data
			return super(Input, self).insert_text("", from_undo=from_undo)

		return super(Input, self).insert_text(substring, from_undo=from_undo)

class InputHolder(BoxLayout):
	def __init__(self, main_window):
		super(InputHolder, self).__init__(size=(5, 40), size_hint=(1, None))
		#self.add_widget(Input(main_window))
		
class ShowRecsPanel(BoxLayout):
	def __init__(self, main_window):
		super(ShowRecsPanel, self).__init__(size=(5,40), size_hint=(0.5, None), pos_hint={"center_x": 0.5, "center_y": 0.5})
		button = Button(text='Show Recommendations', size=(150, 50))
		button.bind(on_press=main_window.show_recommendations)
		self.add_widget(button)

class Recs(FloatLayout):
	def __init__(self, recommendations):
		super(Recs, self).__init__(size_hint=(1, 1), pos=(0,0))

		self.create_background()
		self.bind(pos=self.update_rect, size=self.update_rect)

		self.recommendations = recommendations
		stack = StackLayout(pos=(0,0), size_hint=(1,1), padding=[0, 50, 0, 0], orientation="tb-lr")
		title_index = list(recommendations.columns).index("title")

		for row in recommendations.values:
			print(row[title_index])
			stack.add_widget(Label(text=row[title_index], size=(300, 30), size_hint=(1, None)))

		self.add_widget(stack)
	
	def create_background(self):
		with self.canvas.before:
			Color(0, 0, 0, 1)
			self.rect = Rectangle(size=self.size,
			                      pos=self.pos)

	def update_rect(self, instance, value):
		self.rect.pos = self.pos
		self.rect.size = self.size

class MainWindow(FloatLayout):
	def __init__(self):
		super(MainWindow, self).__init__(pos=(0,0), size_hint=(1,1))
		self.add_widget(SearchWindow())

class SearchWindow(BoxLayout):
	def __init__(self, **kwargs):
		super(SearchWindow, self).__init__(orientation='vertical')
		button_label = Label(text='Rate this movie:', size_hint=(1, None), 
			halign='center', valign="bottom", font_size=30, size_hint_max_y=40) 

		self.current_movie = MovieData('Mad Max (1979)')
		self.mpi = Movie_Poster_Info(self.current_movie)

		self.ratings = {}
		self.bp = Button_Panel()
		self.bp.bind(on_1_button=self.rate_movie_1)
		self.bp.bind(on_2_button=self.rate_movie_2)
		self.bp.bind(on_3_button=self.rate_movie_3)
		self.bp.bind(on_4_button=self.rate_movie_4)
		self.bp.bind(on_5_button=self.rate_movie_5)

		self.add_widget(InputHolder(self))
		self.add_widget(ShowRecsPanel(self))
		self.add_widget(self.mpi)
		self.add_widget(button_label)
		self.add_widget(self.bp)

	def show_recommendations(self, arg):
		cols = user_movie_matrix.columns

		new_row = [0] * len(cols)

		for key in self.ratings.keys():
			index_of_col = list(cols).index(key)
			new_row[index_of_col] = self.ratings[key]

		tmp = user_movie_matrix
		new_or_last_index = len(tmp)

		if new_or_last_index != self_id: # we add a new user to the end of the list, unless we've already run this, in which case we replace the row
			new_or_last_index += 1

		tmp.loc[new_or_last_index] = new_row
		user_movie_matrix.update(tmp) # call update so it's visible to other places this is imported

		recs = svd.recommend(self_id)[1]
		recs_widget = Recs(recs)
		self.parent.add_widget(recs_widget)
		anchor_tl = AnchorLayout(anchor_x='left', anchor_y='top')

		close_button = Button(text='x', size=(30,30), size_hint=(None, None))
		close_button.bind(on_press=lambda _: self.parent.remove_widget(recs_widget))
		anchor_tl.add_widget(close_button)
		recs_widget.add_widget(anchor_tl)

	def rate_movie(self, rating):
		self.ratings[self.current_movie.id] = rating

	def rate_movie_1(self, obj):
		self.rate_movie(1)

	def rate_movie_2(self, obj):
		self.rate_movie(2)

	def rate_movie_3(self, obj):
		self.rate_movie(3)

	def rate_movie_4(self, obj):
		self.rate_movie(4)

	def rate_movie_5(self, obj):
		self.rate_movie(5)

class Button_Panel(FloatLayout):
	def __init__(self, **kwargs):
		super(Button_Panel, self).__init__(size_hint=(1, None), size_hint_max_y=150)

		self.register_event_type('on_1_button')
		self.register_event_type('on_2_button')
		self.register_event_type('on_3_button')
		self.register_event_type('on_4_button')
		self.register_event_type('on_5_button')

		buttons_layout=BoxLayout(size_hint=(1,None))
		self.buttons = []

		self.button_1 = StarButton()
		self.buttons.append(self.button_1)
		self.button_1.bind(on_press=self.button_pressed(1))
		self.button_1.bind(on_enter=self.select_1_button)
		self.button_1.bind(on_exit=self.unselect_1_button)		

		self.button_2 = StarButton()
		self.buttons.append(self.button_2)
		self.button_2.bind(on_press=self.button_pressed(2))
		self.button_2.bind(on_enter=self.select_2_button)
		self.button_2.bind(on_exit=self.unselect_2_button)

		self.button_3 = StarButton()
		self.buttons.append(self.button_3)
		self.button_3.bind(on_press=self.button_pressed(3))
		self.button_3.bind(on_enter=self.select_3_button)
		self.button_3.bind(on_exit=self.unselect_3_button)

		self.button_4 = StarButton()
		self.buttons.append(self.button_4)
		self.button_4.bind(on_press=self.button_pressed(4))
		self.button_4.bind(on_enter=self.select_4_button)
		self.button_4.bind(on_exit=self.unselect_4_button)

		self.button_5 = StarButton()
		self.buttons.append(self.button_5)
		self.button_5.bind(on_press=self.button_pressed(5))
		self.button_5.bind(on_enter=self.select_5_button)
		self.button_5.bind(on_exit=self.unselect_5_button)

		buttons_layout.add_widget(self.button_1)
		buttons_layout.add_widget(self.button_2)
		buttons_layout.add_widget(self.button_3)
		buttons_layout.add_widget(self.button_4)
		buttons_layout.add_widget(self.button_5)

		self.add_widget(buttons_layout)

	"""def on_size(self, *args):
		self.canvas.before.clear()
		with self.canvas.before:
			Color(1, 1, 1, 1,)
			Rectangle(pos=self.pos, size=self.size)"""

	def select_prev_buttons(self, button_num):
		for i in range(0, button_num):
			self.buttons[i].change_image_selected()

	def unselect_prev_buttons(self, button_num):
		for i in range(0, button_num):
			self.buttons[i].change_image_unselected()

	def select_1_button(self, *args):
		self.select_prev_buttons(1)

	def select_2_button(self, *args):
		self.select_prev_buttons(2)

	def select_3_button(self, *args):
		self.select_prev_buttons(3)

	def select_4_button(self, *args):
		self.select_prev_buttons(4)

	def select_5_button(self, *args):
		self.select_prev_buttons(5)
	
	def unselect_1_button(self, *args):
		self.unselect_prev_buttons(1)

	def unselect_2_button(self, *args):
		self.unselect_prev_buttons(2)

	def unselect_3_button(self, *args):
		self.unselect_prev_buttons(3)

	def unselect_4_button(self, *args):
		self.unselect_prev_buttons(4)

	def unselect_5_button(self, *args):
		self.unselect_prev_buttons(5)

	def button_pressed(self, rating):
		return lambda _: self.dispatch("on_" + str(rating) + "_button")

	def on_1_button(self, *args):
		pass

	def on_2_button(self, *args):
		pass

	def on_3_button(self, *args):
		pass

	def on_4_button(self, *args):
		pass

	def on_5_button(self, *args):
		pass

class MovieInfo(BoxLayout):
	def __init__(self, movie, **kwargs):
		super(MovieInfo, self).__init__(orientation='vertical')

		anchor_tl = AnchorLayout(anchor_x='left', anchor_y='top', 
			padding=(0, 50, 0, 0))
		anchor_ml = AnchorLayout(anchor_x='left', anchor_y='top', 
			padding=(20, 0, 20, 0))

		grid_layout = GridLayout(cols=2, spacing=(20,0), size_hint_max_y=240, 
			size_hint_min_y=200, padding=(0,20,0,20))

		self.genres_label = Builder.load_string(data_label)
		self.release_date_label = Builder.load_string(data_label)

		self.genres_label.text='Genres:'
		self.release_date_label.text='Release Date:'

		self.overview_info = Builder.load_string(wrap_info)
		anchor_ml.add_widget(self.overview_info)

		self.genres_info = Builder.load_string(data_info)
		self.release_date_info = Builder.load_string(data_info)

		self.overview_info.text=movie.overview
		self.genres_info.text=movie.genres_as_str()
		self.release_date_info.text=movie.year

		grid_layout.add_widget(self.genres_label)
		grid_layout.add_widget(self.genres_info)
		grid_layout.add_widget(self.release_date_label)
		grid_layout.add_widget(self.release_date_info)

		anchor_tl.add_widget(grid_layout)

		self.add_widget(anchor_tl)
		self.add_widget(anchor_ml)

	def update(self, movie):
		self.overview_info.text=movie.overview
		self.genres_info.text=movie.genres_as_str()

class Poster(BoxLayout):
	def __init__(self, movie, **kwargs):
		super(Poster, self).__init__(orientation='vertical')
		self.title_label = Label(text=movie.title, size_hint=(1, None), 
			halign='center',valign="middle", font_size=50)
		self.title_label.bind(texture_size=self.title_label.setter('size'))
		self.poster = PosterImage(source=movie.poster_url)
		self.add_widget(self.title_label)
		self.add_widget(self.poster)

	def update(self, movie):
		self.title_label.text = movie.title
		self.poster.source = movie.poster_url


class Movie_Poster_Info(BoxLayout):
	def __init__(self, movie, **kwargs):
		super(Movie_Poster_Info, self).__init__(orientation='horizontal', 
			padding=(20,0,0,0))

		self.poster = Poster(movie)
		self.movie_info = MovieInfo(movie)
		self.add_widget(self.poster)
		self.add_widget(self.movie_info)

	def update(self, movie):
		self.poster.update(movie)
		self.movie_info.update(movie)

class PosterImage(AsyncImage):
	pass

class StarButton(ButtonBehavior, Image):
	def __init__(self, **kwargs):
		super(StarButton, self).__init__(**kwargs)
		self.register_event_type('on_enter')
		self.register_event_type('on_exit')
		self.register_event_type('on_exit_left')
		self.hovered = BooleanProperty(False)
		self.border_point = ObjectProperty(None)
		Window.bind(mouse_pos=self.on_mouse_pos)
		self.source = 'gui_assets/empty_star.png'

	#def on_press(self):
		#self.source = 'gui_assets/empty_star.png'
	
	#def on_release(self):
		#self.source = 'gui_assets/empty_star.png'

	def on_mouse_pos(self, *largs):
		if not self.get_root_window():
			return

		pos = self.to_widget(*largs[1])
		inside = self.collide_point(*pos)

		if self.hovered == inside:
			return

		self.hovered = inside
		self.border_point = pos

		left = self.center_x - self.texture_size[0] / 2
		x = self.border_point[0]

		if inside:
			self.source = 'gui_assets/filled_star.png'
			self.dispatch('on_enter')
		else:
			self.source = 'gui_assets/empty_star.png'
			if(x > left):
				self.dispatch('on_exit')


	def change_image_selected(self):
		self.source = 'gui_assets/filled_star.png'

	def change_image_unselected(self):
		self.source = 'gui_assets/empty_star.png'

	def on_enter(self, *args):
		pass
	
	def on_exit(self, *args):
		pass
	
	def on_exit_left(self, *args):
		pass

class MovieSuggestion(App):
	def build(self):
		mw = MainWindow()
		return mw

MovieSuggestion().run()