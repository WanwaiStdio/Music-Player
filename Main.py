from kivy.config import Config
Config.set('graphics','resizable', False)
from os import stat
from kivy import clock
from kivy.app import App
from kivy.core import text
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from threading import Thread
from playlist import playlist
from playingqueue import playingqueue
from song import song
from HoverImage import HoverImage
import SlideNorn
from kivymd.app import MDApp
from SongBox import SongBox
import pyautogui
from PlaylistBox import PlaylistBox
from kivy.core.text import LabelBase
from DownLoadButton import DownloadURL

# Add Font
LabelBase.register(name='sf',fn_regular='archive/finalFont.ttf')

# Load KV File
Builder.load_file('main.kv')
# Get user screen display size
user_width, user_height = pyautogui.size()
# # Adjust Window size when start
# app_width = 1024
# app_height = 768
# Window.size = (app_width,app_height)
# Window._set_window_pos((user_width/2)-(app_width/2),(user_height/2)-(app_height/2))
Window.maximize()
fullpath=[]
f = open("archive/song/yoursongpath.txt", "r+",encoding='utf-8')

for x in f:
    print(x)
    if x[-1:] == "\n":
        s=song(x[:-1])
        fullpath.append(s)
f.close()
yoursong = playlist("yoursong",fullpath)

templist=[]
playlistlist=[]
playlistlist.append(yoursong)
f = open("archive/song/playlist.txt", "r+",encoding='utf-8')
for x in f:
    if x[-1:] == "\n":
        if x[0] is "%":
            playlistlist.append(playlist(x[1:-1],templist.copy()))
            templist=[]
            continue
        s=song(x[:-1])
        templist.append(s)
f.close()
print(playlistlist[0].name)

class MainGridLayout(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f'Main width = {self.width}')
        print(f'Main height = {self.height}')
        # self.start_stop.bind(on_press=self.press)
        self.play.bind(on_press=self.press)
        self.next.bind(on_press=self.nextpress)
        self.prev.bind(on_press=self.prevpress)
        self.bool = False
        Clock.schedule_interval(lambda dt: self.playtimeUpdate(), 0.1)
        self.queue = playingqueue()
        self.queue.chooseplaylist(yoursong)
        self.queue.addfromqueuefirstsong()
        #Load Song
        self.soundpath = self.queue.nowplaying.getpath()
        print(self.queue.nowplaying)
        self.sound = SoundLoader.load(self.soundpath)
        self.ids.song_name.text=self.queue.nowplaying.getname()
        self.ids.song_name.font_name = 'sf'
        self.volume = 0.25
        #seek
        self.seekvalue = 0
        self.playtimeUpdateBool = True
        #slidenorninit
        self.playlistindex=0
        self.showsong(yoursong)
        self.showplaylist(playlistlist)
        self.ids.playlist_name.text = f'{playlistlist[self.playlistindex].name}'
        download_box = DownloadURL()
        self.ids.playlist_name_box.add_widget(download_box)
        
    def showplaylist(self,playlistlist):
        self.ids.playlistslide.clear_widgets()
        for i in range(len(playlistlist)):
            lb = PlaylistBox(i,playlistlist[i].name)
            self.ids.playlistslide.add_widget(lb)
            lb.bind(on_press=self.selectplaylist)

    def showsong(self,playlist): #spiderman
        self.ids.sn.clear_widgets()
        for i in range(len(playlist.playlist)):
            t = playlist.playlist[i].time
            new_t = (t//60) + ((t%60)/100)
            new_t = format(new_t,'.2f')
            time_text = f'{new_t}'
            lb = SongBox(i+1,playlist.playlist[i].name,time_text)
            self.ids.sn.add_widget(lb)
            lb.bind(on_press=self.selectsong)

    def slide_it(self, *args):
        self.volume = float(args[1]/100)
        self.sound.volume = self.volume

    def valuechange(self,*args):
        self.seekvalue=args[1]

    def notupdate(self,*args):
        print("ontouchdown")
        self.playtimeUpdateBool=False

    def seek(self, *args):
        if self.playtimeUpdateBool is False:
            self.playtimeUpdateBool = True
            print("ontouchup")
            #print (sound.state)
            #print (sound.length)
            if (self.sound.state=='play'):
                print(self.seekvalue)
                self.sound.seek(self.seekvalue*self.sound.length/10000)
            else:
                self.sound.play()
                self.sound.seek(self.seekvalue*self.sound.length/10000)
                self.sound.stop()

    def press(self, instance):
            if self.bool is False:
                self.play = Button(text='Play')
                self.bool = True
                self.sound.play()
                self.sound.volume = self.volume
            else:
                self.play = Button(text='Stop')
                self.bool = False
                self.sound.stop()

    def nextpress(self,instance):
        if self.queue.isEmpty():
            print("QueueIsEmpty")
            return
        self.sound.stop()
        self.queue.addfromqueue()
        self.soundpath = self.queue.nowplaying.getpath()
        self.sound = SoundLoader.load(self.soundpath)
        self.ids.song_name.text=self.queue.nowplaying.getname()
        self.sound.play()
        self.sound.volume=self.volume
        self.playtimeUpdate()

    def prevpress(self,instance):
        print(self.queue.isStackEmpty())
        if self.queue.isStackEmpty():
            print("StackIsEmpty")
            return
        self.sound.stop()
        self.queue.addfromstack()
        self.soundpath = self.queue.nowplaying.getpath()
        self.sound = SoundLoader.load(self.soundpath)
        self.ids.song_name.text=self.queue.nowplaying.getname()
        self.sound.play()
        self.sound.volume=self.volume
        self.playtimeUpdate()

    def playtimeUpdate(self):
        self.sound.volume=self.volume
        if self.playtimeUpdateBool is True:
            #print(self.ids.playtime.value_pos)
            value=int(self.sound.get_pos()*10000/self.sound.length)
            if value>=9990:
                self.nextpress("instance")
                value=0
            self.ids.playtime.value=value

    def repeatState(self, state):
        if state.state == 'down':
            print(f'Repeat is ON')
        else:
            print(f'Repeat is OFF')

    def shuffleState(self, state):
        if state.state == 'down':
            print(f'Shuffle is ON')
        else:
            print(f'Shuffle is OFF')

    def selectsong(self,*args):
        self.sound.stop()
        index=args[0].index
        self.queue.chooseplaylist(playlistlist[self.playlistindex])
        print(self.queue.musicqueue)
        self.queue.addfromqueuefirstsong()
        for i in range(index):
            self.queue.addfromqueue()
        print(self.queue.nowplaying)
        self.soundpath = self.queue.nowplaying.getpath()
        self.sound = SoundLoader.load(self.soundpath)
        self.ids.song_name.text=self.queue.nowplaying.getname()
        self.sound.play()
        self.sound.volume=self.volume
        self.playtimeUpdate()
        self.bool=True

    def selectplaylist(self,*args):
        index=args[0].index
        self.playlistindex=index
        self.showsong(playlistlist[index])
        self.ids.playlist_name.text = f'{playlistlist[index].name}'

    def Searched_Song(self, text="", search=False):
        for songg in self.queue.originalplaylist:
            if text in songg.name:
                print(songg.name)

# class MainWidget(Widget):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

class MainApp(MDApp):
    def build(self):
        self.title = 'Wanwai Player'
        self.icon = 'Icon/title.png'
        return MainGridLayout()
if __name__ == "__main__":
    MainApp().run()