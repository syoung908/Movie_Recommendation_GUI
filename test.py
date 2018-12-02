from kivy.app import App
from kivy.event import EventDispatcher

class MyEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_test')
        super(MyEventDispatcher, self).__init__(**kwargs)

    def do_something(self, value):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        self.dispatch('on_test', value)

    def on_test(self, *args):
        print(f'I am dispatched {args}')

def my_callback(value, *args):
    print(f"Hello, I got an event!{args}")


ev = MyEventDispatcher()
ev.bind(on_test=my_callback)
ev.do_something('test')