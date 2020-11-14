from kivy.uix.image import Image
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from kivy import metrics
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock as kivyClock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.app import App
from common.screen import ScreenManager, Screen
from common.gfxutil import topleft_label, CEllipse, KFAnim, AnimGroup, CLabelRect
from common.core import BaseWidget, run
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.behaviors import ButtonBehavior
  
## not necessary while using .kv file 
from kivy.uix.checkbox import CheckBox 
# To do some manupulation on window impoet window 
from kivy.core.window import Window 
from kivy.factory import Factory
from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'height', '450')
Config.set('graphics', 'width', '800')


font_sz = metrics.pt(20)
button_sz = metrics.pt(100)
THEME = {
    "red": Color(1,0,0),
    "dark-red": Color(.5,0,0),
    "white": Color(1, 1, 1),
    "black": Color(0, 0, 0),
}


class StartPopup(Popup):
    def __init__(self, **kwargs):
        super(StartPopup, self).__init__(**kwargs)
        self.


class GenrePopup(Popup):
    pass

class IntroScreen(Screen):
    image = "data/bedroom.jpg"
    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs)
        self.genre_popup = GenrePopup()

class ImageButton(ButtonBehavior, Image):
    pass


class Vocagen(App):

    def build(self):
        Window.size = (800, 450)
        intro = IntroScreen(name='intro')
        return intro

    def on_start(self, **kwargs):
        start_popup = StartPopup()
        start_popup.open()

class SampBoxLayout(BoxLayout):
    # Callback for the checkbox
    def checkbox_click(self, instance, value):
        if value is True:
            print("Checkbox Checked")
        else:
            print("Checkbox Unchecked")



if __name__ == "__main__":
    Vocagen().run()
