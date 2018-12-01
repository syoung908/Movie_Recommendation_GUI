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


IMAGES_URLS_2 = ['https://upload.wikimedia.org/wikipedia/commons/c/c3/Jordan_by_Lipofsky_16577.jpg',
    'https://kivy.org/doc/stable/_images/animation__animate__py1.png',
    'https://i.stack.imgur.com/c77oX.png']

IMAGES_URLS = ['https://upload.wikimedia.org/wikipedia/commons/c/c3/Jordan_by_Lipofsky_16577.jpg' for _ in range(5)]


class InfinityScrollView(ScrollView):
    def __init__(self):
        super(InfinityScrollView, self).__init__(size_hint=(1, None), 
            height=600, pos_hint={'center_x': .5, 'center_y': .5})
        self.layout = GridLayout(rows=1, spacing=10, size_hint_x=None)
        #self.layout = BoxLayout(orientation='horizontal', size_hint_x=None)
        
        self.layout.bind(minimum_width=self.layout.setter('width'))
        #self.image_queue = image_queue

        for url in IMAGES_URLS:
            img = img = AsyncImageButton(url)
            self.layout.add_widget(img)
        self.add_widget(self.layout)
            
    def on_scroll_move(self, touch):
        if self.scroll_x > 1:
            self.upload_images()
        return super(InfinityScrollView, self).on_scroll_move(touch)

    def upload_images(self):
        layout = self.children[0]
        layout_childrens = len(layout.children)
        for url in IMAGES_URLS:
            img = AsyncImageButton(url)
            layout.add_widget(img)
        bar_position = layout_childrens / (layout_childrens + len(IMAGES_URLS))
        self.scroll_x = 100 * bar_position
        self.effect_x.value = self.effect_x.min * bar_position

class AsyncImageButton(ButtonBehavior, AsyncImage):
    def __init__(self, url):
        super(AsyncImageButton, self).__init__(source=url, size_hint=(None, 1), width=240)
        self.original_width = self.width
        self.hovered = BooleanProperty(False)
        self.border_point = ObjectProperty(None)
        Window.bind(mouse_pos=self.on_mouse_pos)
    
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
            


class InfiniteScrollApp(App):
    def build(self):
        root = InfinityScrollView()
        return root


if __name__ == '__main__':
    InfiniteScrollApp().run()


