from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.properties import NumericProperty

Builder.load_string('''                               
<Loading>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: root.angle
            axis: 0, 0, 1
            origin: root.center
    canvas.after:
        PopMatrix

    Image:
        source: 'gui_assets/Rolling.png'
        size_hint: None, None
        size: 100, 100
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
''')

class Loading(FloatLayout):
    angle = NumericProperty(0)
    def __init__(self, **kwargs):
        super(Loading, self).__init__(**kwargs)
        anim1 = Animation(angle = 360, duration=2) 
        anim1 += Animation(angle = 360, duration=2)
        anim1.repeat = True

        anim2 = Animation(opacity=0.3, width=100, duration=0.6)
        anim2 += Animation(opacity=1, width=400, duration=0.8)
        anim2.repeat = True

        anim1.start(self)
        anim2.start(self)

    def on_angle(self, item, angle):
        if angle == 360:
            item.angle = 0

class LoadingMessage(Label):
    def __init__(self, **kwargs):
        super(LoadingMessage, self).__init__(**kwargs)
        self.pos_hint={'center_x': 0.5, 'center_y': 0.35}
        self.font_size=25

class TestApp(App):
    def build(self):
        return Loading()

#TestApp().run()