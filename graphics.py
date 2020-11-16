#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.abspath('../lib'))

from common.core import BaseWidget, run, lookup

from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.window import Window

class InteractiveImage(Image):
    def __init__(self, **kwargs):
        super(InteractiveImage, self).__init__(**kwargs, keep_data=True, allow_stretch=True, keep_ratio=False)
        self.callback = None
        Window.bind(mouse_pos=self.on_mouse_pos)


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

    def on_mouse_pos(self, window, pos):
        if self.collide_point(*pos):
            self.color = [1, 1, 1, 0.5]
        else:
            self.color = [1, 1, 1, 1]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if not self.callback is None:
                self.callback()

class Scene(BaseWidget):
    def __init__(self):
        super(Scene, self).__init__()

        # Background
        self.background = Image(allow_stretch=True, keep_ratio=False)
        self.background.source = "./data/scene/background.png"
        self.add_widget(self.background)

        # Amp
        self.amp = InteractiveImage()
        self.amp.source = "./data/scene/amp.png"
        self.amp.set_callback(lambda: print("amp"))
        self.add_widget(self.amp)

        # Computer
        self.computer = InteractiveImage()
        self.computer.source = "./data/scene/computer.png"
        self.computer.set_callback(lambda: print("computer"))
        self.add_widget(self.computer)

        # Guitar
        self.guitar = InteractiveImage()
        self.guitar.source = "./data/scene/guitar.png"
        self.guitar.set_callback(lambda: print("guitar"))
        self.add_widget(self.guitar)

        # Mic
        self.mic = InteractiveImage()
        self.mic.source = "./data/scene/mic.png"
        self.mic.set_callback(lambda: print("mic"))
        self.add_widget(self.mic)
        
        # Radio
        self.radio = InteractiveImage()
        self.radio.source = "./data/scene/radio.png"
        self.radio.set_callback(lambda: print("radio"))
        self.add_widget(self.radio)
        
        # File cabinet
        self.storage = InteractiveImage()
        self.storage.source = "./data/scene/storage.png"
        self.storage.set_callback(lambda: print("storage"))
        self.add_widget(self.storage)

    def on_layout(self, win_size):
        self.background.size = win_size
        self.amp.size = win_size
        self.computer.size = win_size
        self.guitar.size = win_size
        self.mic.size = win_size
        self.radio.size = win_size
        self.storage.size = win_size

if __name__ == "__main__":
    run(Scene())
