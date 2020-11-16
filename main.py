#!/usr/bin/env python3

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
from kivy.uix.dropdown  import DropDown 

from common.screen import ScreenManager, Screen
from common.gfxutil import topleft_label, CEllipse, KFAnim, AnimGroup, CLabelRect
from common.core import BaseWidget, run
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.behaviors import ButtonBehavior
from ashika_play_area.input_demo import *
  
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


class VolumePopup(Popup):
    def __init__(self, **kwargs):
        super(VolumePopup, self).__init__(**kwargs)


class InstrumentPopup(Popup):
    def __init__(self, **kwargs):
        super(InstrumentPopup, self).__init__(**kwargs)
        self.dropdown = DropDown()



class CustomDropDown(DropDown):
    pass


class GenrePopup(Popup):
    pass


class RecordPopup(Popup):
    def __init__(self, record_callback, play_callback):
        super(RecordPopup, self).__init__()
        self.record_callback = record_callback
        self.play_callback = play_callback
        self.mic_meter = MeterDisplay((140, 90),  100, (-96, 0), (.1, .9, .3))
        self.mic_graph = GraphDisplay((200, 90), 100, 160, (-96, 0), (.1, .9, .3))

        self.pitch_meter = MeterDisplay(
            (140, 210), 100, (30, 90), (.9, .1, .3))
        self.pitch_graph = GraphDisplay(
            (200, 210), 100, 160, (30, 90), (.9, .1, .3))

        self.canvas.add(self.mic_meter)
        self.canvas.add(self.mic_graph)
        self.canvas.add(self.pitch_meter)
        self.canvas.add(self.pitch_graph)
        

class IntroScreen(BaseWidget):
    image = "data/bedroom.jpg"
    def __init__(self):
        super(IntroScreen, self).__init__()
        self.genre_popup = GenrePopup()
        self.volume_popup = VolumePopup()
        self.record_popup = RecordPopup(self.init_recording, self.play_recording)
        self.instruments_popup = InstrumentPopup()

        self.audio = Audio(2, input_func=self.receive_audio,
                           num_input_channels=1)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)
        self.pitch = PitchDetector()
        self.recorder = VoiceAudioWriter('data')

        self.cur_pitch = 0

        # Note Scheduler
        self.synth = Synth('data/FluidR3_GM.sf2')

        # create TempoMap, AudioScheduler
        self.tempo_map = SimpleTempoMap(120)
        self.sched = AudioScheduler(self.tempo_map)

        # connect scheduler into audio system
        self.mixer.add(self.sched)
        self.sched.set_generator(self.synth)

        # Note Sequencers
        self.seq = []

        # live Generator
        self.live_wave = None

    def on_update(self):
        self.audio.on_update()


    def receive_audio(self, frames, num_channels):
        assert(num_channels == 1)

        # Microphone volume level, take RMS, convert to dB.
        # display on meter and graph
        rms = np.sqrt(np.mean(frames ** 2))
        rms = np.clip(rms, 1e-10, 1)  # don't want log(0)
        db = 20 * np.log10(rms)      # convert from amplitude to decibels
        self.record_popup.mic_meter.set(db)
        self.record_popup.mic_graph.add_point(db)

        # pitch detection: get pitch and display on meter and graph
        self.cur_pitch = self.pitch.write(frames)
        self.record_popup.pitch_meter.set(self.cur_pitch)
        self.record_popup.pitch_graph.add_point(self.cur_pitch)

        # record audio
        self.recorder.add_audio(frames, num_channels)


    def init_recording(self):
        data = self.recorder.toggle()
        if data:
            wave_gen, filename, duration_midi = data
            for i in range(len(duration_midi)):
                if duration_midi[i][0] < 0.12:
                    duration_midi[i] = (duration_midi[i][0], 0)
            duration_midi = harmony.harmonize(duration_midi)
            self.live_wave = wave_gen
            print([[i[1] for i in j] for j in duration_midi])

            tempo = 120
            multiplier = 1/60*tempo*480
            converted_midi_duration = [[(i*multiplier, j)
                                        for i, j in k] for k in duration_midi]

            for i in converted_midi_duration:
                self.seq.append(NoteSequencer(
                    self.sched, self.synth, 1, (0, 0), i, True))

    def play_recording(self):
        for i in self.seq:
            i.start()
        if self.live_wave:
            self.mixer.add(self.live_wave)

class ImageButton(ButtonBehavior, Image):
    pass


class Vocagen(App):

    def build(self):
        Window.size = (800, 450)
        intro = IntroScreen()
        return intro

    def on_start(self, **kwargs):
        start_popup = StartPopup()
        start_popup.open()




if __name__ == "__main__":
    Vocagen().run()
