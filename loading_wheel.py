from kivy.app import App
from kivy.lang import Builder
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
        anim = Animation(angle = 360, duration=2) 
        anim += Animation(angle = 360, duration=2)
        anim.repeat = True
        anim.start(self)

    def on_angle(self, item, angle):
        if angle == 360:
            item.angle = 0


#class TestApp(App):
#    def build(self):
#        return Loading()

#TestApp().run()