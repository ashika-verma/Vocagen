#!/usr/bin/env python3

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
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.button import Button 
from kivy.uix.dropdown  import DropDown 

from common.screen import ScreenManager, Screen
from common.gfxutil import topleft_label, CEllipse, KFAnim, AnimGroup, CLabelRect
from common.core import BaseWidget, run
from common.metro import Metronome
from common.wavesrc import WaveFile
from common.clock import Clock, SimpleTempoMap, AudioScheduler, kTicksPerQuarter, quantize_tick_up
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior
from ashika_play_area.input_demo import *

from graphics import Scene

  
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


class Checkboxes():
    def __init__(self, labels_and_defaults):
        self.labels = {}
        self.init_active = {}
        for group in labels_and_defaults:
            labels, index_active = labels_and_defaults[group]
            self.labels[group] = labels
            self.init_active[group] = index_active

    def get_labels_dict(self):
        return self.labels.copy()

    def get_init_active_dict(self):
        return self.init_active.copy()


##################### INSTRUMENTS!! #########################
# {group: (labels_list, default_index_selected)}
INSTRUMENT_CHECKBOXES = Checkboxes({
    "high voice": (["piano", "violin", "guitar", "flute"], 0),
    "mid voice": (["piano", "viola", "guitar"], 0),
    "low voice": (["piano", "cello", "bass"], 0)
})
ALL_PIANO_SELECTED = {
    "high voice": 0,
    "mid voice": 0,
    "low voice": 0
}
ORCHESTRA = {
    "high voice": 1,
    "mid voice": 1,
    "low voice": 1
}
POP = {
    "high voice": 0,
    "mid voice": 2,
    "low voice": 2
}
# ... and so on! keep filling this out
# use set_checkboxes(ORCHESTRA) to set checkboxes
##############################################################

######################## GENRES!! ############################
GENRE_CHECKBOXES = Checkboxes({
    "GENRE": (["classical", "pop", "Coming\nsoon!"], 0)
})
##############################################################

class StartPopup(Popup):
    def __init__(self, **kwargs):
        super(StartPopup, self).__init__(**kwargs)


class VolumePopup(Popup):
    def __init__(self, callback):
        super(VolumePopup, self).__init__()
        self.slider_callback = callback  # takes in (slider_id, value)



class CheckboxPopup(Popup):
    def __init__(self, callback, title, checkboxes):
        super(CheckboxPopup, self).__init__()
        self.instrument_callback = callback
        
        self.title = title
        self.checkbox_labels = checkboxes.get_labels_dict()

        # set up checkboxes
        self.checkboxes = {}
        max_items = -1 # for checkbox layout
        for group in self.checkbox_labels:
            max_items = max(len(self.checkbox_labels[group]), max_items)
            self.checkboxes[group] = []

        # creating the checkbox layout
        self.layout = GridLayout(cols = (max_items+1))
        for i in self.checkbox_labels:
            self.layout.add_widget(SimpleLabel(text=i))
            checkbox_list = self.checkbox_labels[i]

            # fills in checkboxes and labels
            for j in range(len(checkbox_list)):
                box_layout = BoxLayout()
                item = checkbox_list[j]
                current_checkbox = CheckBox(group = i)
                current_checkbox.bind(on_press=self.on_checkbox_active)
                self.checkboxes[i].append(current_checkbox)
                box_layout.add_widget(current_checkbox)
                box_layout.add_widget(SimpleLabel(text=item))
                self.layout.add_widget(box_layout)

            # creates fillers
            for j in range(max_items-len(checkbox_list)):
                self.layout.add_widget(BoxLayout())
        self.content = self.layout


        # sets the current choices as active
        self.set_checkboxes(checkboxes.get_init_active_dict())
        
    def set_checkboxes(self, option_dict):
        '''
        Takes in a dictionary of group: index
        looks like self.init_active
        sets new items as active
        '''
        for group in option_dict:
            new_index = option_dict[group]
            group_checkboxes = self.checkboxes[group]
            group_checkboxes[new_index]._do_press()

    def on_checkbox_active(self, checkbox_instance):
        if checkbox_instance.active:
            group = checkbox_instance.group
            index = self.checkboxes[group].index(checkbox_instance)
            label = self.checkbox_labels[group][index]
            print(group, label)
            self.instrument_callback(label, group)
        else:
            checkbox_instance._do_press()
            

class SimpleLabel(Label):
    pass


class StoragePopup(Popup):
    def __init__(self, get_wave_callback, set_wave_callback):
        super(StoragePopup, self).__init__()
        self.get_wave_callback = get_wave_callback
        self.set_wave_callback = set_wave_callback
        self.wave_gens = {}

        # on record button press, select a wave generator
        # on save button press, set a wave generator to current wave
        # on play button press, set live wave to selected button
    
    def on_play_button_press(self):
        current_index_selected = self.get_selected_index()
        if current_index_selected < 0:
            return
        if current_index_selected not in self.wave_gens.keys():
            return
        # get the saved recording
        new_wave_gen, sequencers = self.wave_gens[current_index_selected]
        # replace the live wave in the larger scene
        self.set_wave_callback(new_wave_gen, sequencers)

    def on_save_button_press(self):
        current_index_selected = self.get_selected_index()
        if current_index_selected<0:
            return

        # save the current live wave into self.wave_gens[current_index_selected]
        current_wave_and_seqs = self.get_wave_callback()
        if not current_wave_and_seqs:
            return
        self.wave_gens[current_index_selected] = current_wave_and_seqs

        # indicate whether a wave generator is saved at a certain index


    def get_selected_index(self):
        # gets the index of the button which is presently selected
        # returns -1 if no button is selected
        widgets = ToggleButtonBehavior.get_widgets('storage')
        index = -1
        for idx in range(len(widgets)):
            widget = widgets[idx]
            if widget.state == "down":
                index = idx
        return index

    



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
        self.genre_popup = CheckboxPopup(self.genre_callback, "GENRE", GENRE_CHECKBOXES)
        self.volume_popup = VolumePopup(self.slider_callback)
        self.record_popup = RecordPopup(self.init_recording, self.toggle_playing)
        self.instruments_popup = CheckboxPopup(self.instrument_callback, "INSTRUMENTS", INSTRUMENT_CHECKBOXES)
        self.storage_popup = StoragePopup(self.get_live_wave, self.set_live_wave)
        self.audio = Audio(2, input_func=self.receive_audio,num_input_channels=1)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)
        self.pitch = PitchDetector()
        self.recorder = VoiceAudioWriter('data')
        self.playing = False
        self.recording = False
        self.cmd = None

        self.scene = Scene()
        self.add_widget(self.scene)
        self.scene.foreground.radio.set_callback(self.genre_popup.open)
        self.scene.foreground.amp.set_callback(self.volume_popup.open)
        self.scene.foreground.mic.set_callback(self.record_popup.open)
        self.scene.foreground.guitar.set_callback(self.instruments_popup.open)
        self.scene.foreground.storage.set_callback(self.storage_popup.open)

        self.cur_pitch = 0
        self.midi_notes = None
        
        self.bass = [((40,60),(0,0)),((43,64),(0,42)),((28,48),(0,33))]
        self.tenor = [((52,69),(0,0)),((52,69),(0,41)),((45,64),(0,26))]
        self.alto = [((57,77),(0,0)),((60,79),(0,40)),((52,72),(0,29)),((67,86),(0,73))]
        self.instruments = [self.bass,self.tenor,self.alto]
        self.genre = 'pop'
        
        self.indices = [0,0,0]

        # Note Scheduler
        self.synth = Synth('data/FluidR3_GM.sf2')

        # create TempoMap, AudioScheduler
        self.tempo_map = SimpleTempoMap(120)
        self.sched = AudioScheduler(self.tempo_map)
        self.metro = Metronome(self.sched, self.synth)
        self.start_tick = None

        # connect scheduler into audio system
        self.mixer.add(self.sched)
        self.sched.set_generator(self.synth)

        # Note Sequencers
        self.seq = [None, None, None]

        # live Generator
        self.live_wave = None

        # current .wav file
        self.current_wave_file = None
        
    def genre_callback(self, value, label):
        self.genre = value
        if value == 'classical':
            self.instruments_popup.set_checkboxes(ORCHESTRA)
            self.indices = [1,1,1]
            self.instrument_callback(None, None)
        if value == 'pop':
            self.instruments_popup.set_checkboxes(POP)
            self.indices = [2,2,0]
            self.instrument_callback(None, None)
            
    def instrument_callback(self, value, label):
        if label == 'high voice':
            self.indices[2] = ['piano','violin','guitar','flute'].index(value)
        if label == 'mid voice':
            self.indices[1] = ['piano','viola','guitar'].index(value)
        if label == 'low voice':
            self.indices[0] = ['piano','cello','bass'].index(value)
        if self.live_wave is not None:
            for i in self.seq:
                i.stop()
                self.live_wave.reset()
                #reharmonize and update NoteSequencers
            duration_midi = harmony.harmonize(self.midi_notes, self.genre, brange = self.bass[self.indices[0]][0],
                                              trange = self.tenor[self.indices[1]][0],
                                              arange = self.alto[self.indices[2]][0])
            tempo = self.tempo_map.get_tempo()
            multiplier = 1/60*tempo*480
            converted_midi_duration = [[(i*multiplier, j)
                                        for i, j in k] for k in duration_midi]
            
            for i in range(3):
                self.seq[i] = NoteSequencer(
                    self.sched, self.synth, i+1, self.instruments[i][self.indices[i]][1], 
                    converted_midi_duration[i+1], self.scene.add_note_sprite, True)
            if self.playing:
                self.play_recording(1)
        
    def slider_callback(self, voice, value):
        val = int(value)
        idx = [ "bass","tenor", "alto", "melody"].index(voice)+1
        if idx < 4:
            self.synth.cc(idx, 7, val)
        else:
            if self.live_wave:
                self.live_wave.set_gain(val/100)

    def on_update(self):
        self.audio.on_update()
        self.scene.on_update()

    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'm':
            self.metro.toggle()
        bpm_adj = lookup(keycode[1], ('up', 'down'), (10, -10))
        if bpm_adj and not self.playing and not self.recording:
            new_tempo = max(self.tempo_map.get_tempo() + bpm_adj, 30)
            self.tempo_map.set_tempo(new_tempo, self.sched.get_time())

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
        if not self.recording:
            self.start_tick = self.sched.get_tick()
        data = self.recorder.toggle()
        if not data:
            self.recording = True
            if self.live_wave is not None:
                try:
                    self.mixer.remove(self.live_wave)
                except:
                    pass
            for i in self.seq:
                if i is not None:
                    i.stop()
            self.playing = False
        else:
            self.recording = False
            stop_tick = self.sched.get_tick()
            wave_gen, filename, duration_midi = data
            self.current_wave_file = WaveFile(filename)
            #ignore short notes
            i=0
            while i<len(duration_midi):
                if duration_midi[i][0] < 0.1:
                    duration_midi[i-1] = (duration_midi[i][0]+duration_midi[i-1][0], duration_midi[i-1][1])
                    duration_midi.pop(i)
                else:
                    i+=1
            duration_midi[0] = (duration_midi[0][0] - .1, duration_midi[0][1])
            ticks = [(int(note[0] * 480 * self.tempo_map.get_tempo() / 60), note[1])
                     for note in duration_midi]
            ticks[0] = (ticks[0])
            duration_midi = []
            tick_length = sum(i[0] for i in ticks)
            curr_beat = int(480 - self.start_tick%480 + .22 * 8 * self.tempo_map.get_tempo()) % 480
            ind = 0
            ticks_passed = 0
            while tick_length > 0:
                tot = 0
                times = {}
                while tot < curr_beat and ind < len(ticks):
                    left = ticks[ind][0] - ticks_passed
                    if left > curr_beat - tot:
                        ticks_passed += curr_beat-tot
                        if ticks[ind][1] in times:
                            times[ticks[ind][1]] += curr_beat-tot
                        else:
                            times[ticks[ind][1]] = curr_beat-tot
                        tot = curr_beat
                    else:
                        tot += left
                        ticks_passed = 0
                        if ticks[ind][1] in times:
                            times[ticks[ind][1]] += left
                        else:
                            times[ticks[ind][1]] = left
                        ind += 1
                big = 80
                note = 0
                print(times)
                for guy in times:
                    if times[guy] > big and guy != 0:
                        note = guy
                        big = times[guy]
                duration_midi.append((60*curr_beat/480/self.tempo_map.get_tempo(), note))
                tick_length -= curr_beat
                curr_beat = min(480, tick_length)
            duration_midi = [(0.1,0)] + duration_midi
            self.midi_notes = duration_midi
            #find harmonies
            self.live_wave = wave_gen
            good = False
            for i in duration_midi:
                if i[1] > 0:
                    good = True
                    break
            if good:
                duration_midi = harmony.harmonize(duration_midi, self.genre, brange = self.bass[self.indices[0]][0],
                                                  trange = self.tenor[self.indices[1]][0],
                                                  arange = self.alto[self.indices[2]][0])
                #print([[i[1] for i in j] for j in duration_midi])
    
                # cheat to use SimpleTempoMap
                tempo = self.tempo_map.get_tempo()
                multiplier = 1/60*tempo*480
                converted_midi_duration = [[(i*multiplier, j)
                                            for i, j in k] for k in duration_midi]
                #make NoteSequencers
                for i in range(3):
                    self.seq[i] = NoteSequencer(
                        self.sched, self.synth, i+1, self.instruments[i][self.indices[i]][1], 
                        converted_midi_duration[i+1], self.scene.add_note_sprite, True)
                    
    def play_recording(self, tick):
        for i in self.seq:
            if i is not None:
                i.start()
        if self.live_wave:
            self.live_wave.play()
            if self.live_wave not in self.mixer.generators:
                self.mixer.add(self.live_wave)

    def start_playing(self):
        if self.playing:
            return
        self.metro.stop()
        self.playing = True
        
        now = self.sched.get_tick()
        next_beat = quantize_tick_up(now, kTicksPerQuarter*4)
        self.cmd = self.sched.post_at_tick(self.play_recording, next_beat)

    def stop_playing(self):
        if not self.playing:
            return

        self.playing = False
        for i in self.seq:
            i.stop()
        self.live_wave.reset()

        self.sched.cancel(self.cmd)
        self.cmd = None

    def toggle_playing(self):
        print(self.playing)
        if self.playing:
            self.stop_playing()
        else:
            self.start_playing()

    def get_live_wave(self):
        if self.live_wave:
            return WaveGenerator(self.current_wave_file, True), self.seq.copy()

    def set_live_wave(self, new_live_wave, note_sequencers):
        if self.live_wave:
            if self.live_wave is not None:
                try:
                    self.mixer.remove(self.live_wave)
                except:
                    pass

            for i in self.seq:
                if i is not None:
                    i.stop()
            self.seq = note_sequencers
            for i in self.seq:
                if i is not None:
                    i.start()
            self.live_wave = new_live_wave
            self.mixer.add(self.live_wave)
            self.start_playing()
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
