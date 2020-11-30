#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.abspath('../lib'))

from common.core import BaseWidget, run, lookup
from common.gfxutil import topleft_label, CEllipse, KFAnim, AnimGroup

from kivy.uix.image import Image
from kivy.core.image import Image as Img
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.graphics.instructions import InstructionGroup
from random import random, randint



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


class FadingMusicNote(InstructionGroup):
    def __init__(self, pos=(0, 0)):
        super(FadingMusicNote, self).__init__()
        self.body = Rectangle(pos=pos, size=(10, 10), texture=Img('./data/scene/eightnote.png').texture)
        self.pop_anim = KFAnim((0, self.body.size[0]), (.5, 0))
        self.pos_anim = KFAnim((0, pos[0], pos[1]), (.5, pos[0]+100, pos[1]+randint(-30, 30)))
        self.add(self.body)
        self.time = 0
        self.active = False
        self.on_update(0)

    def on_update(self, dt):
        # the disappearing animation just reduces the size
        new_size = self.pop_anim.eval(self.time)
        new_pos = self.pos_anim.eval(self.time)
        self.body.size = (new_size, new_size)
        self.body.pos = new_pos
        self.time += dt
        return self.pop_anim.is_active(self.time)

    def start_anim(self):
        self.active = True


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

        # Flying music notes
        self.anim_group = AnimGroup()
        self.canvas.add(self.anim_group)
        self.anim_group.add(FadingMusicNote())

    def on_layout(self, win_size):
        self.background.size = win_size
        self.amp.size = win_size
        self.computer.size = win_size
        self.guitar.size = win_size
        self.mic.size = win_size
        self.radio.size = win_size
        self.storage.size = win_size

    def on_update(self):
        self.anim_group.on_update()

    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'a':
            self.anim_group.add(FadingMusicNote())


if __name__ == "__main__":
    run(Scene())
