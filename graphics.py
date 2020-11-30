#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.abspath('../lib'))

import time
import random

from common.core import BaseWidget, run, lookup
from common.gfxutil import topleft_label, CEllipse, KFAnim, AnimGroup

from kivy.uix.image import Image
from kivy.core.image import Image as Img
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.graphics.instructions import InstructionGroup


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
        self.pos_anim = KFAnim((0, pos[0], pos[1]), (.5, pos[0]+100, pos[1]+random.randint(-30, 30)))
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

class FlyingCarWidget(Image):
    def __init__(self, init_pos, size, velocity, **kwargs):
        super(FlyingCarWidget, self).__init__(**kwargs)
        self.init_pos = init_pos
        self.size = size

        self.velocity = velocity
        self.t = time.time()

        self.anim_delay = 0.5

    def is_visible(self):
        x, y = self.pos
        w, h = self.size

        if self.velocity > 0:
            return x < Window.width
        else:
            return x + w > 0

    def on_update(self):
        t = time.time() - self.t
        x_0, y_0 = self.init_pos
        self.pos = (x_0 + self.velocity * t, y_0)

class FlyingCarGeneratorWidget(BaseWidget):

    car_assets = (
        ("./data/scene/food_truck.gif", "./data/scene/food_truck_reverse.gif"),
        ("./data/scene/nyan_cat.gif", "./data/scene/nyan_cat_reverse.gif"),
        ("./data/scene/warp_ship.gif", "./data/scene/warp_ship_reverse.gif"),
        ("./data/scene/superman.png", "./data/scene/superman_reverse.png"),
        ("./data/scene/flying_delorean.png", "./data/scene/flying_delorean_reverse.png"),
    )

    def __init__(self, y_range):
        super(FlyingCarGeneratorWidget, self).__init__()

        self.y_range = y_range
        self.speed = 90 # pixels/sec
        self.cars = []

        self.t_next_car = 0
        self.max_cars = 5

    def generate_car(self):

        # Choose random car asset
        forward, backward = random.choice(self.car_assets)

        # Choose randomly between forward and backward
        direction = random.choice(["forward", "backward"])
        if direction == "forward":
            source = forward
            velocity = self.speed * random.uniform(0.8, 1.2)
            x_0 = 0
        else:
            source = backward
            velocity = -self.speed * random.uniform(0.8, 1.2)
            x_0 = Window.width

        # Randomly select starting y coordinate
        y_0 = random.uniform(*self.y_range)

        # Construct car widget
        car = FlyingCarWidget((x_0, y_0), (100, 100), velocity)
        car.source = source
        self.cars.append(car)
        self.add_widget(car)


    def on_update(self):

        # Process updates for each car
        for car in self.cars:
            car.on_update()

        # Check for cars that have gotten
        cars_to_delete = []
        for i, car in enumerate(self.cars):
            if not car.is_visible():
                cars_to_delete.append(i)

        # Delete complete cars
        for i in cars_to_delete:
            self.remove_widget(self.cars[i])
            del self.cars[i]

        # Generate new cars if there's room and if we haven't
        # recently created a new car
        t_now = time.time()
        if len(self.cars) < self.max_cars and \
           t_now > self.t_next_car:
            self.generate_car()
            self.t_next_car = t_now + random.uniform(1, 5)

class BackgroundWidget(BaseWidget):
    def __init__(self):
        super(BackgroundWidget, self).__init__()

        # Background
        self.background = Image(allow_stretch=True, keep_ratio=False)
        self.background.source = "./data/scene/background.png"
        self.add_widget(self.background)

        self.car_generator = FlyingCarGeneratorWidget((100, 500))
        self.add_widget(self.car_generator)

    def on_layout(self, win_size):
        self.background.size = win_size

    def on_update(self):
        pass

class ForegroundWidget(BaseWidget):
    def __init__(self):
        super(ForegroundWidget, self).__init__()

        # Foreground
        self.foreground = Image(allow_stretch=True, keep_ratio=False)
        self.foreground.source = "./data/scene/foreground.png"
        self.add_widget(self.foreground)

        # Amp
        self.amp = InteractiveImage()
        self.amp.source = "./data/scene/amp.png"
        self.amp.set_callback(lambda: print("amp"))
        self.add_widget(self.amp)

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
        self.foreground.size = win_size
        self.amp.size = win_size
        self.guitar.size = win_size
        self.mic.size = win_size
        self.radio.size = win_size
        self.storage.size = win_size
    

class Scene(BaseWidget):
    def __init__(self):
        super(Scene, self).__init__()

        self.background = BackgroundWidget()
        self.add_widget(self.background)

        self.foreground = ForegroundWidget()
        self.add_widget(self.foreground)

        # Flying music notes
        self.anim_group = AnimGroup()
        self.canvas.add(self.anim_group)
        self.anim_group.add(FadingMusicNote())

    def on_layout(self, win_size):
        self.background.on_layout(win_size)
        self.foreground.on_layout(win_size)

    def on_update(self):
        self.anim_group.on_update()

    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'a':
            self.anim_group.add(FadingMusicNote())


if __name__ == "__main__":
    run(Scene())
