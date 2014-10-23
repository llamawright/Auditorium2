from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.core.audio import Sound
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.adapters.models import SelectableDataItem
from kivy.uix.listview import ListItemButton
import os


class Player():
    pPath = StringProperty();
    pFile = StringProperty();
    sound = ObjectProperty();

    def __init__(self):
        self.loadd = False;

    def loadit(self, pPath, filename):
        if self.loadd == True:
            self.sound.stop()
            self.sound.unload()
            self.loadd = False
        self.paused = False
        self.pPath = pPath
        self.filename = filename
        self.sound = SoundLoader.load(os.path.join(self.pPath, self.filename))
        self.loadd = True

    def playit(self):
        if self.loadd == True:
            self.paused = False
            self.sound.play()

    def stopit(self):
        if self.loadd == True:
            self.paused = False
            self.sound.stop()

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



class MainForm(BoxLayout):
    pList = ListProperty(['one', 'two', 'three'])
    pDir = StringProperty('')
    pPath = StringProperty('/')
    music = Player()
    pNumb = NumericProperty(-1);

    def __init__(self, **kwargs):
        super(MainForm, self).__init__(**kwargs)
        self.list_view.adapter.bind(on_selection_change=self.selection_changed)
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
        for i in range(len(self.list_view.adapter.data)):
            if self.list_view.adapter.get_view(i).text==self.list_view.adapter.selection[0].text:
                self.pNumb= i
                break
        self.music.loadit(self.pPath, self.list_view.adapter.get_view(self.pNumb).text)

    def next(self):
        if self.pNumb >= -1 and self.pNumb < len(self.list_view.adapter.data):
            self.pNumb += 1
            #load up the play button
            #self.music.loadit(self.pPath, self.list_view.adapter.get_view(self.pNumb).text)
        if self.pNumb < len(self.list_view.adapter.data):
            self.list_view.adapter.get_view(self.pNumb).trigger_action(duration=0)
        else:
            self.music.stopit()

    def playit(self):
        self.music.playit()

    def scroll(self):
        self.list_view.adapter.scroll_to(47)

class AuditoriumApp(App):
    def build(self):
        return MainForm()

if __name__ == '__main__':
    AuditoriumApp().run()
