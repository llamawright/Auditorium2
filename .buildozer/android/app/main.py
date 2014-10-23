from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView
from kivy.core.audio import SoundLoader


class MainForm(BoxLayout):
    pass

    def loadit(self):
        global sound
        sound = SoundLoader.load('emma.mp3')

    def loadit2(self):
        global sound
        sound = SoundLoader.load('aladdin.wav')

    def playit(self):
        global sound
        sound.play()

    def stopit(self):
        sound.stop()

class AuditoriumApp(App):
    def build(self):
        return MainForm()

if __name__ == '__main__':
    AuditoriumApp().run()
