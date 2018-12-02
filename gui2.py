from kivy.config import Config
Config.set('graphics', 'width', '1050')
Config.set('graphics', 'height', '850')
Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

from kivy.app import App
from kivy.clock import Clock, _default_time as time
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout

from infinite_scroll import InfinityScrollView
from loading_wheel import Loading, LoadingMessage
from movie_data import MovieData, get_random_movie
from user_dataframe import user_movie_matrix
import svd

from collections import deque
from threading import Thread
from typing import Deque

self_id = user_movie_matrix.index.values[-1] + 1

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        button_panel = BoxLayout(orientation='horizontal', padding=(10,10,10,10),
            height=120, size_hint=(1, None), spacing=10)
        main_panel = BoxLayout(orientation='vertical')

        self.user_rating_button = UserRatingButton()
        self.user_rating_button.bind(on_press=self.open_popup)

        self.get_recs_button = CustomButton('gui_assets/movie_icon.png', 
            'Get Recommendations')
        self.get_recs_button.bind(on_press=self.load_recommendations)

        self.get_rand_movie_button = CustomButton('gui_assets/question_mark.png',
            'Get Random Movie')
        self.get_rand_movie_button.bind(on_press=self.get_random)

        self.search_button = CustomButton('gui_assets/search.png', 
            'Search Movies')

        self.switch_to_recs_button = CustomButton('gui_assets/go_to.png', 
            'View Recommendations')
        self.switch_to_recs_button.bind(on_press=self.go_to_recs)


        self.rating_popup = RatingPopUp(self)
        self.rating_popup.bind(on_dismiss=self.popup_closed)

        self.current_movie = get_random_movie()
        self.rated_current_movie = False
        self.current_rating = -1

        self.mpi = Movie_Poster_Info(self.current_movie)

        button_panel.add_widget(self.user_rating_button)
        button_panel.add_widget(self.get_recs_button)
        button_panel.add_widget(self.get_rand_movie_button)
        button_panel.add_widget(self.search_button)
        button_panel.add_widget(self.switch_to_recs_button)

        main_panel.add_widget(self.mpi)
        main_panel.add_widget(button_panel)

        self.add_widget(main_panel)

    def get_random(self, obj):
        self.user_rating_button.change_label_prompt()
        self.current_movie = get_random_movie()
        self.refresh()

    def refresh(self):
        self.mpi.update(self.current_movie)
        self.rated_current_movie = False
        self.current_rating = -1

        if not self.rated_current_movie:
            self.user_rating_button.change_label_prompt()
        else:
            self.user_rating_button.change_label_rating(self.current_rating)

    def open_popup(self, obj):
        self.rating_popup.open()

    def popup_closed(self, obj):
        if not self.rated_current_movie:
            self.user_rating_button.change_label_prompt()
        else:
            self.user_rating_button.change_label_rating(self.current_rating)

    def rate_movie(self, rating):
        self.manager.get_screen('recs').ratings[self.current_movie.id] = rating

    def rate_movie_1(self, obj):
        self.rate_movie(1)
        self.user_rating_button.change_label_rating(1)
        self.current_rating = 1
        self.rated_current_movie = True
    
    def rate_movie_2(self, obj):
        self.rate_movie(2)
        self.user_rating_button.change_label_rating(2)
        self.current_rating = 2
        self.rated_current_movie = True
    
    def rate_movie_3(self, obj):
        self.rate_movie(3)
        self.user_rating_button.change_label_rating(3)
        self.current_rating = 3
        self.rated_current_movie = True
        
    def rate_movie_4(self, obj):
        self.rate_movie(4)
        self.user_rating_button.change_label_rating(4)
        self.current_rating = 4
        self.rated_current_movie = True

    def rate_movie_5(self, obj):
        self.rate_movie(5)
        self.user_rating_button.change_label_rating(5)
        self.current_rating = 5
        self.rated_current_movie = True

    def highlight_movie_1(self, obj):
        self.user_rating_button.change_label_rating(1)
    
    def highlight_movie_2(self, obj):
        self.user_rating_button.change_label_rating(2)

    def highlight_movie_3(self, obj):
        self.user_rating_button.change_label_rating(3)

    def highlight_movie_4(self, obj):
        self.user_rating_button.change_label_rating(4)

    def highlight_movie_5(self, obj):
        self.user_rating_button.change_label_rating(5)
    
    def unhighlight(self, obj):
        self.user_rating_button.change_label_rating(0)
    
    def load_recommendations(self, obj):
        self.manager.transition.direction = 'left'
        self.manager.current = 'recs'
        self.manager.get_screen('recs').load_recommendations()
    
    def go_to_recs(self, obj):
        self.manager.transition.direction = 'left'
        self.manager.current = 'recs'
    
class RecScreen(Screen):
    def __init__(self, **kwargs):
        super(RecScreen, self).__init__(**kwargs)
        self.ratings = {}
        self.recommendation_queue = Deque['Movie_Data']()
        self.no_recs_label = Label(pos_hint={'center_x': 0.5, 'center_y': 0.5},
            font_size=30, text='No Recommendations')
        button_panel = BoxLayout(orientation='horizontal', padding=(10,10,10,10),
            height=120, size_hint=(1, None), spacing=10)
        self.add_widget(self.no_recs_label)
        self.back_button = CustomButton('gui_assets/go_back.png', 
            'Go Back')
        self.back_button.bind(on_press=self.go_back)
        self.back_button.pos_hint={'x': 0, 'y': 0}
        button_panel.add_widget(self.back_button)
        self.add_widget(button_panel)

    def load_recommendations(self):
        self.remove_widget(self.no_recs_label)
        self.loading_wheel = Loading()
        self.loading_message = LoadingMessage(text='Generating Recommendations')
        self.add_widget(self.loading_wheel)
        self.add_widget(self.loading_message)
        Thread(target=self.generate_recommendations).start()
        
    def generate_recommendations(self):
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

        recs = svd.recommend(self_id, n_recommendations=20, print_output=False)[1]
        
        for rec in recs.values:
            self.recommendation_queue.append(MovieData(rec[0]))

        self.remove_widget(self.loading_wheel)
        self.remove_widget(self.loading_message)
        self.update_rec_window()
    
    def update_rec_window(self):
        recs_view = InfinityScrollView(self.recommendation_queue)
        recs_view.bind(on_select_movie=self.view_movie_details)
        self.add_widget(recs_view)

    def view_movie_details(self, *args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'main'
        self.manager.get_screen('main').current_movie=MovieData(args[1])
        self.manager.get_screen('main').refresh()
    
    def go_back(self, *args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'main'

class PosterImage(AsyncImage):
    pass

class RatingPopUp(Popup):
    def __init__(self, parent_panel):
        super(RatingPopUp, self).__init__(title='', separator_height=0,
            size_hint=(None, None), size=(400,120), 
            background_color=(0, 0, 0, 0))
        self.parent_panel = parent_panel
        self.auto_dismiss = True
        self.layout = BoxLayout()
        self.bp = StarButtonPanel()

        self.bp.bind(on_1_button=parent_panel.rate_movie_1)
        self.bp.bind(on_2_button=parent_panel.rate_movie_2)
        self.bp.bind(on_3_button=parent_panel.rate_movie_3)
        self.bp.bind(on_4_button=parent_panel.rate_movie_4)
        self.bp.bind(on_5_button=parent_panel.rate_movie_5)
        self.bp.bind(on_any_button_pressed=self.button_pressed)

        self.bp.bind(on_1_highlight=parent_panel.highlight_movie_1)
        self.bp.bind(on_2_highlight=parent_panel.highlight_movie_2)
        self.bp.bind(on_3_highlight=parent_panel.highlight_movie_3)
        self.bp.bind(on_4_highlight=parent_panel.highlight_movie_4)
        self.bp.bind(on_5_highlight=parent_panel.highlight_movie_5)
        self.bp.bind(on_unhighlight=parent_panel.unhighlight)
        
        self.layout.add_widget(self.bp)

        self.add_widget(self.layout)
    
    def button_pressed(self, obj):
        self.dismiss()
    
class StarButtonPanel(BoxLayout):
    def __init__(self, **kwargs):
        super(StarButtonPanel, self).__init__(size_hint=(0.5, None), 
            size_hint_max_y=150)

        self.register_event_type('on_1_button')
        self.register_event_type('on_2_button')
        self.register_event_type('on_3_button')
        self.register_event_type('on_4_button')
        self.register_event_type('on_5_button')
        self.register_event_type('on_any_button_pressed')

        self.register_event_type('on_1_highlight')
        self.register_event_type('on_2_highlight')
        self.register_event_type('on_3_highlight')
        self.register_event_type('on_4_highlight')
        self.register_event_type('on_5_highlight')
        self.register_event_type('on_unhighlight')

        buttons_layout=BoxLayout(size_hint=(1,None))
        self.buttons = []

        self.button_1 = StarButton(first_button=True)
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

    def select_prev_buttons(self, button_num):
        for i in range(0, button_num):
            self.buttons[i].change_image_selected()

    def unselect_prev_buttons(self, button_num):
        for i in range(0, button_num):
            self.buttons[i].change_image_unselected()

    def select_1_button(self, *args):
        self.select_prev_buttons(1)
        self.dispatch('on_1_highlight')

    def select_2_button(self, *args):
        self.select_prev_buttons(2)
        self.dispatch('on_2_highlight')

    def select_3_button(self, *args):
        self.select_prev_buttons(3)
        self.dispatch('on_3_highlight')

    def select_4_button(self, *args):
        self.select_prev_buttons(4)
        self.dispatch('on_4_highlight')

    def select_5_button(self, *args):
        self.select_prev_buttons(5)
        self.dispatch('on_5_highlight')
    
    def unselect_1_button(self, *args):
        self.unselect_prev_buttons(1)
        self.dispatch('on_unhighlight')

    def unselect_2_button(self, *args):
        self.unselect_prev_buttons(2)
        self.dispatch('on_unhighlight')

    def unselect_3_button(self, *args):
        self.unselect_prev_buttons(3)
        self.dispatch('on_unhighlight')

    def unselect_4_button(self, *args):
        self.unselect_prev_buttons(4)
        self.dispatch('on_unhighlight')

    def unselect_5_button(self, *args):
        self.unselect_prev_buttons(5)
        self.dispatch('on_unhighlight')

    def button_pressed(self, rating):
        return lambda _: self.dispatch("on_" + str(rating) + "_button")

    def on_any_button_pressed(self, *args):
        self.unselect_prev_buttons(5)

    def on_1_button(self, *args):
        self.dispatch('on_any_button_pressed')

    def on_2_button(self, *args):
        self.dispatch('on_any_button_pressed')

    def on_3_button(self, *args):
        self.dispatch('on_any_button_pressed')

    def on_4_button(self, *args):
        self.dispatch('on_any_button_pressed')

    def on_5_button(self, *args):
        self.dispatch('on_any_button_pressed')
    
    def on_1_highlight(self, *args):
        pass

    def on_2_highlight(self, *args):
        pass

    def on_3_highlight(self, *args):
        pass

    def on_4_highlight(self, *args):
        pass

    def on_5_highlight(self, *args):
        pass
    
    def on_unhighlight(self, *args):
        pass

class CustomButton(ButtonBehavior, FloatLayout):
    def __init__(self, image, label):
        super(CustomButton, self).__init__(size_hint = (None, None), 
            size =(160, 100))

        self.bind(pos=self.draw_button)

        self.icon = Image(source=image, pos_hint={'center_x': 0.5, 
            'center_y': 0.6}, size_hint=(None, None))

        self.button_label = Label(text=label, size_hint=(0.5, None), 
            halign='center', valign="top",font_size=12,
            pos_hint={'center_x': 0.5, 'center_y': 0.1}) 

        Window.bind(mouse_pos=self.on_mouse_pos)
        self.hovered = BooleanProperty(False)
        self.add_widget(self.icon)
        self.add_widget(self.button_label)

    def draw_button(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(.2, .2, .2)
            Rectangle(pos=self.pos, size=self.size)

    def on_mouse_pos(self, *largs):
        if not self.get_root_window():
            return

        pos = self.to_widget(*largs[1])
        inside = self.collide_point(*pos)
        
        if self.hovered == inside:
            return
            
        self.hovered = inside
        
        if inside:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(.5, .5, .5)
                Rectangle(pos=self.pos, size=self.size)
        else:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(.2, .2, .2)
                Rectangle(pos=self.pos, size=self.size)

class UserRatingButton(CustomButton):
    def __init__(self, **kwargs):
        super(UserRatingButton, self).__init__('gui_assets/empty_star.png',
        '',)

        self.icon.pos_hint={'x': 0, 'center_y': .5}
        self.icon.size_hint=(None, None)
        
        self.button_label.pos_hint={'right': 1, 'center_y': 0.1}

        self.rating_label = Label(text='Rate This Movie', size_hint=(0.5, None), 
            halign='center', valign="top", font_size=15, 
            pos_hint={'right': 1, 'center_y': .5}) 
        self.rating_label.text_size=(self.button_label.width, None)

        self.add_widget(self.rating_label)

    def change_label_rating(self, rating):
        self.icon.source = 'gui_assets/filled_star.png'
        self.rating_label.text = str(rating)
        self.rating_label.font_size = 40
        self.button_label.text = 'Your Rating'

    def change_label_prompt(self):
        self.icon.source = 'gui_assets/empty_star.png'
        self.rating_label.text = 'Rate This Movie'
        self.rating_label.font_size = 15
        self.button_label.text = ''

class StarButton(ButtonBehavior, Image):
    def __init__(self, first_button=False):
        super(StarButton, self).__init__()
        self.first_button = first_button
        self.register_event_type('on_enter')
        self.register_event_type('on_exit')
        self.register_event_type('on_exit_left')
        self.hovered = BooleanProperty(False)
        self.border_point = ObjectProperty(None)
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.source = 'gui_assets/empty_star.png'

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
            if (x > left) or self.first_button:
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

class MovieInfo(StackLayout):
    def __init__(self, movie, **kwargs):
        super(MovieInfo, self).__init__(orientation='lr-tb', padding=(20,20))

        self.genre_tags_layout = StackLayout(spacing=(10, 10))
        self.update_genre_tags(movie)

        self.title_label = WrapLabel(movie.title, 35, bold=True)
        self.overview_label = WrapLabel('Overview', 20, bold=True)
        self.genres_label = WrapLabel('Genres', 20, bold=True)
        self.release_date_label = WrapLabel('Release Date', 20, bold=True)
        self.runtime_label = WrapLabel('Runtime', 20, bold=True)
        self.popularity_label = WrapLabel('Popularity', 20, bold=True)
        self.budget_label = WrapLabel('Budget', 20, bold=True)
        self.revenue_label = WrapLabel('Revenue', 20, bold=True)

        self.overview_info = WrapLabel(movie.overview, 15)
        self.genres_info = WrapLabel(movie.genres_as_str(), 15)
        self.release_date_info = WrapLabel(movie.release_date_as_str(), 15)
        self.runtime_info = WrapLabel(str(movie.runtime) + ' minutes', 15)
        self.popularity_info = WrapLabel(str(movie.popularity), 15)
        self.budget_info = WrapLabel(movie.budget_as_str(), 15)
        self.revenue_info = WrapLabel(movie.revenue_as_str(), 15)

        self.add_widget(self.title_label)
        self.add_widget(WrapLabel(' ', 15, bold=True))
        self.add_widget(self.overview_label)
        self.add_widget(self.overview_info)
        self.add_widget(WrapLabel(' ', 10, bold=True))
        self.add_widget(self.release_date_label)
        self.add_widget(self.release_date_info)
        self.add_widget(WrapLabel(' ', 10, bold=True))
        self.add_widget(self.runtime_label)
        self.add_widget(self.runtime_info)
        self.add_widget(WrapLabel(' ', 10, bold=True))
        self.add_widget(self.budget_label)
        self.add_widget(self.budget_info)
        self.add_widget(WrapLabel(' ', 10, bold=True))
        self.add_widget(self.revenue_label)
        self.add_widget(self.revenue_info)
        self.add_widget(WrapLabel(' ', 10, bold=True))
        self.add_widget(self.popularity_label)
        self.add_widget(self.popularity_info)
        self.add_widget(WrapLabel(' ', 10, bold=True))
        self.add_widget(self.genres_label)
        self.add_widget(self.genre_tags_layout)

    def update(self, movie):
        self.title_label.text = movie.title 
        self.overview_info.text = movie.overview
        self.genres_info.text = movie.genres_as_str()
        self.release_date_info.text = movie.release_date_as_str()
        self.runtime_info.text = str(movie.runtime) + ' minutes'
        self.popularity_info.text = str(movie.popularity)
        self.budget_info.text = movie.budget_as_str()
        self.revenue_info.text = movie.revenue_as_str()
        self.update_genre_tags(movie)
        
    def update_genre_tags(self, movie):
        self.genre_tags_layout.clear_widgets()
        for tag in movie.genres:
            self.genre_tags_layout.add_widget(
                GenreLabel(tag, 15))

class Movie_Poster_Info(BoxLayout):
    def __init__(self, movie, **kwargs):
        super(Movie_Poster_Info, self).__init__(orientation='horizontal', 
            padding=(0,20,0,0))

        self.poster = PosterImage(source=movie.poster_url)
        self.movie_info = MovieInfo(movie)
        self.add_widget(self.poster)
        self.add_widget(self.movie_info)

    def update(self, movie):
        self.poster.source = movie.poster_url
        self.movie_info.update(movie)

class WrapLabel(Label):
    def __init__(self, label_text, font_size, bold=False):
        super(WrapLabel, self).__init__(markup=bold, size_hint=(1, None), 
            font_size=font_size)
        
        self.padding_y=(0,10)
        if bold:
            self.text='[b]' + label_text + '[/b]'
        else:
            self.text = label_text

        self.bind(
            width=lambda *x: self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('height')(self, 
                self.texture_size[1]))

class GenreLabel(Label):
    def __init__(self, label_text, font_size):
        super(GenreLabel, self).__init__(font_size=font_size, text=label_text, 
            size_hint=(None, None), height=30, padding_x=20)

        self.bind(pos=self.draw_label, size=self.draw_label)
        self.bind(
            width=lambda *x: self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('width')(self, 
                self.texture_size[0]))

    def draw_label(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(.5, .5, .5)
            Rectangle(pos=self.pos, size=self.size)

class MovieSuggestion(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(RecScreen(name='recs'))
        return sm

MovieSuggestion().run()