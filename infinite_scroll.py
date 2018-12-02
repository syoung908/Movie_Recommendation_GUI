from kivy.app import App
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior

from movie_data import MovieData, get_random_movie
from collections import deque

from typing import Deque


class InfinityScrollView(ScrollView):
    def __init__(self, recommendations):
        super(InfinityScrollView, self).__init__(size_hint=(1, None), 
            height=600, pos_hint={'center_x': .5, 'center_y': .5})
        self.register_event_type('on_select_movie')
        self.layout = GridLayout(rows=1, spacing=10, size_hint_x=None)
        self.layout.bind(minimum_width=self.layout.setter('width'))
        self.movie_queue = recommendations

        for _ in range(0, 4):
            if self.movie_queue:
                movie = self.movie_queue.popleft()
                img = RecMovieButton(self, movie)
                self.layout.add_widget(img)
        self.add_widget(self.layout)
            
    def on_scroll_move(self, touch):
        if self.scroll_x > 1:
            self.upload_images()
        return super(InfinityScrollView, self).on_scroll_move(touch)

    def upload_images(self):
        layout = self.children[0]
        layout_childrens = len(layout.children)
        for _ in range(0, 4):
            if self.movie_queue:
                movie = self.movie_queue.popleft()
                img = RecMovieButton(self, movie)
                layout.add_widget(img)
            else:
                return
        bar_position = layout_childrens / (layout_childrens + 4)
        self.scroll_x = 100 * bar_position
        self.effect_x.value = self.effect_x.min * bar_position
    
    def on_select_movie(self, *args):
        pass

class RecMovieButton(ButtonBehavior, AsyncImage):
    def __init__(self, parent_panel, movie):
        super(RecMovieButton, self).__init__(source=movie.poster_url,
            size_hint=(None, 1), width=240)

        self.parent_panel = parent_panel
        self.original_width = self.width
        self.movie = movie
        self.hovered = BooleanProperty(False)
        self.border_point = ObjectProperty(None)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_press(self):
        self.parent_panel.dispatch('on_select_movie', self.movie.id)

    def on_mouse_pos(self, *largs):
        if not self.get_root_window():
            return

        pos = self.to_widget(*largs[1])
        inside = self.collide_point(*pos)

        if self.hovered == inside:
            return

        self.hovered = inside
        self.border_point = pos

        if inside:
            animation = Animation(width=400, duration=0.3)
            animation.start(self)

        else:
            animation = Animation(width=240, duration=0.3)
            animation.start(self)

#for Testing
class InfiniteScrollApp(App):
    def build(self):
        recommendations = deque()
        for _ in range(0, 20):
            recommendations.append(get_random_movie())
            
        root = InfinityScrollView(recommendations)
        return root


if __name__ == '__main__':
    InfiniteScrollApp().run()


