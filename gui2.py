from kivy.app import App
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

from movie_data import MovieData
from movie_data import get_random_movie

Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        button_panel = BoxLayout(orientation='horizontal', padding=(10,10,10,10),
            height=180, size_hint=(1, None), spacing=10)
        main_panel = BoxLayout(orientation='vertical')

        self.user_rating_button = UserRatingButton()
        self.user_rating_button.bind(on_press=self.open_popup)

        self.get_recs_button = CustomButton('gui_assets/movie_icon.png', 
            'Get Recommendations')
        self.get_recs_button.bind(on_press=self.go_to_recommendations_screen)

        self.get_rand_movie_button = CustomButton('gui_assets/question_mark.png',
            'Get Random Movie')
        self.get_rand_movie_button.bind(on_press=self.get_random)

        self.search_button = CustomButton('gui_assets/search.png', 
            'Search Movies')

        self.rating_popup = RatingPopUp(self)
        self.rating_popup.bind(on_dismiss=self.popup_closed)

        self.current_movie = MovieData('Mad Max (1979)')
        self.rated_current_movie = False
        self.current_rating = -1
        self.ratings = {}

        self.mpi = Movie_Poster_Info(self.current_movie)

        button_panel.add_widget(self.user_rating_button)
        button_panel.add_widget(self.get_recs_button)
        button_panel.add_widget(self.get_rand_movie_button)
        button_panel.add_widget(self.search_button)

        main_panel.add_widget(self.mpi)
        main_panel.add_widget(button_panel)

        self.add_widget(main_panel)

    def get_random(self, obj):
        self.user_rating_button.change_label_prompt()
        self.current_movie = get_random_movie()
        self.mpi.update(self.current_movie)
        self.rated_current_movie = False
        self.current_rating = -1


    def open_popup(self, obj):
        self.rating_popup.open()

    def popup_closed(self, obj):
        if not self.rated_current_movie:
            self.user_rating_button.change_label_prompt()
        else:
            self.user_rating_button.change_label_rating(self.current_rating)

    def rate_movie(self, rating):
        self.ratings[self.current_movie.id] = rating

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
    
    def go_to_recommendations_screen(self, obj):

        self.manager.transition.direction = 'left'
        self.manager.current = 'recs'

class RecScreen(Screen):
    def __init__(self, **kwargs):
        super(RecScreen, self).__init__(**kwargs)
        self.Recommendations = []

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

        print(self.canvas)

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

        with self.canvas.before:
            Color(.2, .2, .2)
            Rectangle(pos=self.pos, size=self.size)

        self.icon = Image(source=image, pos_hint={'center_x': 0.5, 
            'center_y': 0.6}, size_hint=(None, None))

        self.button_label = Label(text=label, size_hint=(0.5, None), 
            halign='center', valign="top",font_size=12,
            pos_hint={'center_x': 0.5, 'center_y': 0.1}) 

        Window.bind(mouse_pos=self.on_mouse_pos)
        self.hovered = BooleanProperty(False)
        self.add_widget(self.icon)
        self.add_widget(self.button_label)

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

class MovieInfo(BoxLayout):
    def __init__(self, movie, **kwargs):
        super(MovieInfo, self).__init__(orientation='vertical')

        anchor_tl = AnchorLayout(anchor_x='left', anchor_y='top', 
            padding=(0, 50, 0, 0))
        anchor_ml = AnchorLayout(anchor_x='left', anchor_y='top', 
            padding=(20, 0, 20, 0))

        grid_layout = GridLayout(cols=2, spacing=(20,0), size_hint_max_y=240, 
            size_hint_min_y=200, padding=(0,20,0,20))

        #self.genres_label = Builder.load_string(data_label)
        #self.release_date_label = Builder.load_string(data_label)

        #self.genres_label.text='Genres:'
        #self.release_date_label.text='Release Date:'

        #self.overview_info = Builder.load_string(wrap_info)
        #anchor_ml.add_widget(self.overview_info)

        #self.genres_info = Builder.load_string(data_info)
        #self.release_date_info = Builder.load_string(data_info)

        #self.overview_info.text=movie.overview
        #self.genres_info.text=movie.genres_as_str()
        #self.release_date_info.text=movie.year

        #grid_layout.add_widget(self.genres_label)
        #grid_layout.add_widget(self.genres_info)
        #grid_layout.add_widget(self.release_date_label)
        #grid_layout.add_widget(self.release_date_info)

        #anchor_tl.add_widget(grid_layout)

        #self.add_widget(anchor_tl)
        #self.add_widget(anchor_ml)

    def update(self, movie):
        pass
        #self.overview_info.text=movie.overview
        #self.genres_info.text=movie.genres_as_str()

class Movie_Poster_Info(BoxLayout):
    def __init__(self, movie, **kwargs):
        super(Movie_Poster_Info, self).__init__(orientation='horizontal', 
            padding=(20,20))

        self.poster = PosterImage(source=movie.poster_url)
        self.movie_info = MovieInfo(movie)
        self.add_widget(self.poster)
        self.add_widget(self.movie_info)

    def update(self, movie):
        self.poster.source = movie.poster_url
        self.movie_info.update(movie)

class MovieSuggestion(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(RecScreen(name='recs'))
        return sm

MovieSuggestion().run()