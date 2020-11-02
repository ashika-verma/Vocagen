#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.abspath('../lib'))

from common.core import BaseWidget, run, lookup

from kivy.uix.image import Image
from kivy.uix.widget import Widget

class InteractiveImage(Image):
    def __init__(self, **kwargs):
        super(InteractiveImage, self).__init__(**kwargs, keep_data=True, allow_stretch=True)
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def collide_point(self, x, y):
        try:
            # Adjust x and y to reflect coordinates within the image
            x = (x - self.x) * self._coreimage.width / self.width
            y = (self.height - (y - self.y)) * self._coreimage.height / self.height
            color = self._coreimage.read_pixel(x, y)
        except:
            color = 0, 0, 0, 0
        if color[-1] > 0:
            return True
        return False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.color = [1, 0, 0, 1.0]
            if not self.callback is None:
                self.callback()

    def on_touch_up(self, touch):
        self.color = [1, 1, 1, 1]

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        # Record button
        self.record_button = InteractiveImage()
        self.record_button.source = "./data/mic.png"
        self.record_button.x = 400
        self.record_button.y = 400
        self.record_button.size = (100, 300)
        self.record_button.set_callback(lambda: print("clicked!"))
        self.add_widget(self.record_button)

if __name__ == "__main__":
    run(MainWidget())
