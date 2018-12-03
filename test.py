from random import sample
from string import ascii_lowercase

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty

data = [
    {
        "ml_position": 1,
        "ml_uid": "129C497D00000062",
        "ml_status_id": 2,
        "machine_id": 13,
        "ml_type_id": 1,
        "id": 2
    },
    {
        "ml_position": 2,
        "ml_uid": "128E2F7D000000DA",
        "ml_status_id": 2,
        "machine_id": 13,
        "ml_type_id": 1,
        "id": 3
    },
    {
        "ml_position": 3,
        "ml_uid": "12D7457D000000CE",
        "ml_status_id": 2,
        "machine_id": 13,
        "ml_type_id": 1,
        "id": 4
    },
    {
        "ml_position": 4,
        "ml_uid": "12B72D7D00000022",
        "ml_status_id": 2,
        "machine_id": 13,
        "ml_type_id": 1,
        "id": 5
    },
    {
        "ml_position": 5,
        "ml_uid": "125F0C730000008A",
        "ml_status_id": 2,
        "machine_id": 13,
        "ml_type_id": 1,
        "id": 6
    },
    {
        "ml_position": 6,
        "ml_uid": "12AB087D0000003A",
        "ml_status_id": 2,
        "machine_id": 13,
        "ml_type_id": 1,
        "id": 7
    },
    {
        "ml_position": 7,
        "ml_uid": "12D7237D00000032",
        "ml_status_id": 2,
        "machine_id": 13,
        "ml_type_id": 1,
        "id": 8
    },
    {
        "ml_position": 8,
        "ml_uid": "12BAED7D00000023",
        "ml_status_id": 2,
        "machine_id": 13,
        "ml_type_id": 1,
        "id": 9
    },
    {
        "ml_position": 9,
        "ml_uid": "125F0C730000008A",
        "ml_status_id": 2,
        "machine_id": 13,
        "ml_type_id": 1,
        "id": 10
    }
]

kv = """
<DataRow@BoxLayout>:
    canvas.before:
        Color:
            rgba: 0.5, 0.5, 0.5, 1
            # rgba: (.0, 0.9, .1, .3) if self.selected else (0.5, 0.5, 0.5, 1)
        Rectangle:
            size: self.size
            pos: self.pos
    ml_uid: ''
    ml_position: ''
    Label:
        text: root.ml_uid
        on_touch_down: pass
    TextInput:
        text: root.ml_position
        multiline: False
        padding_y: ( self.height - self.line_height ) / 2
<Test>:
    canvas:
        Color:
            rgba: 0.3, 0.3, 0.3, 1
        Rectangle:
            size: self.size
            pos: self.pos
    rv: rv
    orientation: 'vertical'
    GridLayout:
        cols: 3
        rows: 2
        size_hint_y: None
        height: dp(108)
        padding: dp(8)
        spacing: dp(16)
        Button:
            text: 'Populate list'
            on_press: root.populate()
        Button:
            text: 'Sort list'
            on_press: root.sort()
        Button:
            text: 'Clear list'
            on_press: root.clear()
        BoxLayout:
            spacing: dp(8)
            Button:
                text: 'Insert new item'
                on_press: root.insert(new_item_input.text)
            TextInput:
                id: new_item_input
                size_hint_x: 0.6
                hint_text: 'ml_uid'
                padding: dp(10), dp(10), 0, 0
        BoxLayout:
            spacing: dp(8)
            Button:
                text: 'Update first item'
                on_press: root.update(update_item_input.text)
            TextInput:
                id: update_item_input
                size_hint_x: 0.6
                hint_text: 'new ml_uid'
                padding: dp(10), dp(10), 0, 0
        Button:
            text: 'Remove first item'
            on_press: root.remove()
    RecycleView:
        id: rv
        scroll_type: ['bars', 'content']
        scroll_wheel_distance: dp(114)
        bar_width: dp(10)
        viewclass: 'DataRow'
        RecycleBoxLayout:
            default_size: None, dp(56)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(2)
"""

Builder.load_string(kv)


class Test(RecycleDataViewBehavior, BoxLayout):

    def populate(self):
        self.rv.data = [{'ml_uid': x['ml_uid'], 'ml_position': str(x['ml_position'])} for x in data]

    def sort(self):
        self.rv.data = sorted(self.rv.data, key=lambda x: x['ml_uid'])

    def clear(self):
        self.rv.data = []

    def insert(self, ml_uid):
        self.rv.data.insert(0, {'ml_uid': ml_uid or 'default ml_uid'})

    def update(self, ml_uid):
        if self.rv.data:
            self.rv.data[0]['ml_uid'] = ml_uid or 'default new value'
            self.rv.refresh_from_data()

    def remove(self):
        if self.rv.data:
            self.rv.data.pop(0)


class TestApp(App):
    def build(self):
        return Test()


if __name__ == '__main__':
    TestApp().run()