#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.abspath('../lib'))

from common.core import BaseWidget, run, lookup

from kivy.uix.image import Image
from kivy.uix.widget import Widget

class InteractiveImage(Image):
    def __init__(self, **kwargs):
        super(InteractiveImage, self).__init__(**kwargs, keep_data=True)

    def collide_point(self, x, y):
        try:
            color = self._coreimage.read_pixel(x - self.x, self.height - (y - self.y))
        except:
            color = 0, 0, 0, 0
        if color[-1] > 0:
            return True
        return False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.color = [1, 0, 0, 1.0]

    def on_touch_up(self, touch):
        self.color = [1, 1, 1, 1]


class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()

        path_to_mic = "./data/mic.png"
        self.mic = InteractiveImage()
        self.mic.source = path_to_mic
        self.mic.size = self.mic.texture.size
        self.add_widget(self.mic)

if __name__ == "__main__":
    run(MainWidget())
