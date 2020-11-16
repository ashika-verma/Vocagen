
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from kivy import metrics
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock as kivyClock
from kivy.uix.image import Image
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
    def __init__(self, callback):
        super(VolumePopup, self).__init__()
        self.slider_callback = callback  # takes in (slider_id, value)


class InstrumentPopup(Popup):
    def __init__(self, **kwargs):
        super(InstrumentPopup, self).__init__(**kwargs)



class CustomDropDown(DropDown):
    pass


class GenrePopup(Popup):
    def __init__(self, callback):
        super(GenrePopup, self).__init__()
        self.callback =  callback
    def checkbox_callback(self, obj, group, label, value):
        self.callback(value, label)
        print(group)



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
        self.volume_popup = VolumePopup(self.slider_callback)
        self.record_popup = RecordPopup(self.init_recording, self.play_recording)
        self.instruments_popup = InstrumentPopup()

        self.audio = Audio(2, input_func=self.receive_audio,
                           num_input_channels=1)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)
        self.pitch = PitchDetector()
        self.recorder = VoiceAudioWriter('data')
        self.playing = False

        self.cur_pitch = 0
        self.midi_notes = None
        
        self.bass = [((40,60),(0,0)),((43,64),(0,42)),((28,48),(0,33))]
        self.tenor = [((52,69),(0,0)),((52,69),(0,41)),((45,64),(0,26))]
        self.alto = [((57,77),(0,0)),((60,79),(0,40)),((52,72),(0,29)),((67,86),(0,73))]
        self.instruments = [self.bass,self.tenor,self.alto]
        
        self.indices = [0,0,0]

        # Note Scheduler
        self.synth = Synth('data/FluidR3_GM.sf2')

        # create TempoMap, AudioScheduler
        self.tempo_map = SimpleTempoMap(120)
        self.sched = AudioScheduler(self.tempo_map)

        # connect scheduler into audio system
        self.mixer.add(self.sched)
        self.sched.set_generator(self.synth)

        # Note Sequencers
        self.seq = [None, None, None]

        # live Generator
        self.live_wave = None
        
    def slider_callback(self, voice, value):
        value = int(value)
        #update values
        if voice == 'alto':
            self.indices[2] = value
        if voice == 'tenor':
            self.indices[1] = value
        if voice == 'bass':
            self.indices[0] = value
        if self.live_wave is not None:
            for i in self.seq:
                i.stop()
            self.live_wave.reset()
            #reharmonize and update NoteSequencers
            duration_midi = harmony.harmonize(self.midi_notes, brange = self.bass[self.indices[0]][0],
                                              trange = self.tenor[self.indices[1]][0],
                                              arange = self.alto[self.indices[2]][0])
            tempo = 120
            multiplier = 1/60*tempo*480
            converted_midi_duration = [[(i*multiplier, j)
                                        for i, j in k] for k in duration_midi]
            
            for i in range(3):
                print(self.instruments[i][self.indices[i]][1])
                self.seq[i] = NoteSequencer(
                    self.sched, self.synth, i+1, self.instruments[i][self.indices[i]][1], 
                    converted_midi_duration[i+1], True)
            if self.playing:
                self.play_recording()

    def on_update(self):
        self.audio.on_update()

    # def slider_callback(id, value):
    #     # TODO 
    #     # ids are ["melody", "alto", "tenor", "bass"]
    #     print(id, value)

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
            #ignore short notes
            for i in range(len(duration_midi)):
                if duration_midi[i][0] < 0.12:
                    duration_midi[i] = (duration_midi[i][0], 0)
            self.midi_notes = duration_midi
            #find harmonies
            duration_midi = harmony.harmonize(duration_midi, brange = self.bass[self.indices[0]][0],
                                              trange = self.tenor[self.indices[1]][0],
                                              arange = self.alto[self.indices[2]][0])
            self.live_wave = wave_gen
            print([[i[1] for i in j] for j in duration_midi])

            # cheat to use SimpleTempoMap
            tempo = 120
            multiplier = 1/60*tempo*480
            converted_midi_duration = [[(i*multiplier, j)
                                        for i, j in k] for k in duration_midi]
            #make NoteSequencers
            for i in range(3):
                self.seq[i] = NoteSequencer(
                    self.sched, self.synth, 1, self.instruments[i][self.indices[i]][1], 
                    converted_midi_duration[i+1], True)

    def play_recording(self):
        self.playing = True
        for i in self.seq:
            if i is not None:
                i.start()
        if self.live_wave:
            self.live_wave.play()
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

Vocagen().run()
