from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.core.audio import Sound
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.adapters.models import SelectableDataItem
from kivy.uix.listview import ListItemButton
from kivy.graphics import Color, Line
from kivy.clock import Clock
import os



class Player():
    pPath = StringProperty()
    pFile = StringProperty()
    sound = ObjectProperty()
    pb = ObjectProperty()

    def __init__(self):
        self.loadd = False
        self.playing = False

    def loadit(self, pPath, filename):
        if self.loadd == True:
            self.sound.stop()
            self.sound.unload()
            self.loadd = False
            self.playing = False
        self.paused = False
        self.pPath = pPath
        self.filename = filename
        self.sound = SoundLoader.load(os.path.join(self.pPath, self.filename))
        self.loadd = True
        self.playing = True

    def playit(self):
        if self.loadd == True:
            self.paused = False
            self.playing = True
            self.sound.play()
            Clock.schedule_interval(self.play_pos, 0.5)

    def play_pos(self, dt):
        if not self.playing:
            return 0
        pos = self.sound.get_pos()
        len = self.sound.length
        far = pos*100/len
        root.ids.pb.value = far
        return far

    def play_not(self, dt):
        return 0

    def stopit(self):
        if self.loadd == True:
            self.paused = False
            self.playing = False
            self.sound.stop()
            Clock.schedule_once(self.play_not)

    def pause(self):
        if self.loadd == True:
            if self.paused:
                #self.sound.volume = 0
                self.sound.play()
                #seek not working
                self.sound.seek(self.pause_at)
                #self.sound.volume = 1
                self.paused = False
            else:
                self.pause_at = self.sound.get_pos()
                self.sound.stop()
                self.paused = True


class EffectButton(BoxLayout):

    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.filename = ''
        self.orientation = 'vertical'
        self.tb = Button()
        self.tb.size_hint_y = 0.66
        self.tb.size_hint_x = 1
        self.lb = Button()
        self.lb.size_hint_y = 0.33
        self.lb.size_hint_x = 1
        self.add_widget(self.tb)
        self.add_widget(self.lb)
        self.bar = []

class MainForm(BoxLayout):
    pList = ListProperty([])
    pDir = StringProperty('')
    pPath = StringProperty('/')
    music = Player()
    pNumb = NumericProperty(-1);

    def __init__(self, **kwargs):
        super(MainForm, self).__init__(**kwargs)
        self.list_view.adapter.bind(on_selection_change=self.selection_changed)
        fxa = self.ids.fxa
        self.butbar = []
        for i in range(8):
            nb = EffectButton()
            bar = []
            nb.tb.color = [ 0, .7, .7, 1]
            nb.lb.color = [ 0, .7, .7, 1]
            nb.tb.text = ''
            nb.tb.seqnum = i
            nb.tb.seqact = True
            nb.lb.text = ''
            nb.lb.seqnum = i
            nb.lb.seqact = False
            nb.tb.bind(on_press=self.action)
            nb.lb.bind(on_press=self.action)
            fxa.add_widget(nb)
            self.butbar.append(nb)
        pass

    class LIButton(ListItemButton):
        def __init__(self, **kwargs):
            ListItemButton.__init__(self, **kwargs)
            self.halign = 'left'
            self.text_size = (375, None)
            self.valign = 'middle'

    def getdir(self):
        fc = FileChooserListView(path=self.pPath)
        p = Popup(title='Open Directory/Folder',
                content=fc,
                size_hint=(0.5,0.5))
        p.bind(on_dismiss=lambda x: self.setDir(fc.path))
        p.open()

    def setDir(self, string):
        string = os.path.normpath(string)
        l = sorted([x for x in os.listdir(string)
                if x[0] != '.'
                and '-' in x
                and (
                x[-4:] == '.wav'
                or
                x[-4:] == '.mp3'
                )])
        self.pList = l
        self.pPath = string
        self.pDir = os.path.basename(self.pPath)
        self.list_view.adapter.bind(on_selection_change=self.selection_changed)
        self.pNumb = -1

    def selection_changed(self, *args):
        t = self.pNumb
        lva = self.list_view.adapter
        if lva.selection:
            for i in range(len(lva.data)):
                if lva.get_view(i).text == lva.selection[0].text:
                    t = i
                    break
            self.load(t)
            # self.music.loadit(self.pPath, lva.get_view(self.pNumb).text)

    def stop(self):
        # stop any music and any effects
        self.music.stopit()
        self.stop_effects()

    def next(self):
        # conveniences for list_view.adapter and total number in adapter
        lva = self.list_view.adapter
        many = len(lva.data)
        # stop any music and any effects
        self.stop()
        # if no more entries that are not effects then exit
        t = self.pNumb + 1
        while t < many and self.is_effect(lva.get_view(t).text):
            t += 1
        if t >= many:
            return
        self.load(t)

    def prev(self):
        lva = self.list_view.adapter
        many = len(lva.data)
        # stop any music and any effects
        self.stop()
        # if no more entries that are not effects then exit
        t = self.pNumb - 1
        while t > 0 and self.is_effect(lva.get_view(t).text):
            t -= 1
        if t < 0:
            return
        self.load(t)


    def load(self, pNumb):
        lva = self.list_view.adapter
        many = len(lva.data)
        if self.pNumb == pNumb:
            return
        self.pNumb = pNumb
        if self.is_effect(lva.get_view(self.pNumb).text):
            self.prev()
        n, t = lva.get_view(self.pNumb).text.split('-',1)
        n = n.strip()
        self.ids.play.text = n + '\n' + t 
        lva.get_view(self.pNumb).trigger_action(duration=0)
        t = self.pNumb + 1
        slot = 0
        while t < many and self.is_effect(lva.get_view(t).text):
            self.load_effect(lva.get_view(t).text, slot)
            t += 1
            slot += 1
        self.music.loadit(self.pPath, lva.get_view(self.pNumb).text)
        if not lva.get_view(self.pNumb).is_selected:
            lva.get_view(self.pNumb).trigger_action(duration=0)


    def playit(self):
        self.music.playit()

    def scroll(self):
        self.list_view.adapter.scroll_to(47)

    def is_effect(self, filename):
        for c in filename:
            if c == '-':
                return False
            if 'A' <= c <=  'Z':
                return True
        return False

    def load_effect(self, filename, slot):
        if slot < 8:
            fullpath = os.path.join( self.pPath, filename)
            self.butbar[slot].filename = fullpath
            t, ext = os.path.splitext(filename)
            n, t = t.split('-', 1)
            n = n.strip()
            t = t.split()
            t = n +'\n' + '\n'.join(t)
            self.butbar[slot].tb.text = t
            self.butbar[slot].lb.text = 'Stop'



    def action(self, obj):

        if obj.seqact:
            if obj.parent.filename == '':
                return
            effect = SoundLoader.load(obj.parent.filename)
            obj.parent.bar.append(effect)
            effect.play()
        else:
            for effect in obj.parent.bar:
                effect.stop()
            obj.parent.bar = []

    def stop_effects(self):
        for obj in self.butbar:
            for effect in obj.bar:
                effect.stop()
            obj.parent.bar = []
            for k in self.butbar:
                k.filename = ''
                k.tb.text = ''
                k.lb.text = ''



class AuditoriumApp(App):
    def build(self):
        global root
        root = MainForm()
        return root

if __name__ == '__main__':
    AuditoriumApp().run()
