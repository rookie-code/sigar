from kivy.app import App

# kivy grafic user interface
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.pagelayout import PageLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager, SwapTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel

# kivy event and animation
from kivy.clock import Clock
from kivy.animation import Animation

# kivy garden object
from kivy.garden.knob import Knob

# kivy propeties
from kivy.properties import NumericProperty, StringProperty

# utility library
import json
import Adafruit_DHT as dht
# kivy start
import kivy
kivy.require('1.0.5')


class MyAnchorLayout(AnchorLayout):
    pass


class LogoImage(Image):
    def __init__(self, **kwargs):
        super(LogoImage, self).__init__(**kwargs)
        #self.beat()
    
    def beat(self, *args):
        animation1 = Animation(opacity=0.3, t="out_bounce", duration=6.)
        animation1 += Animation(opacity=1, t="linear", duration=4.)
        animation1.repeat = True
        animation1.start(self)

    
class DemoApp(App):
    
    def start_data(self):
        with open('./data.json', 'r') as f:
            data = json.load(f)

            self.data_mm["unit_temp"] = data["unit_temp"]
            self.data_mm["max_temp"] = data["max_temp"]
            self.data_mm["max_um"] = data["max_um"]
            self.data_mm["min_temp"] = data["min_temp"]
            self.data_mm["min_um"] = data["min_um"]

        self.update_data_mm()
    
    def changeUnit(self):
        if self.data_mm["unit_temp"] == 'C':
            self.data_mm["unit_temp"] = 'F'
        else:
            self.data_mm["unit_temp"] = 'C'
        self.update_data_mm()

    def update_data_mm(self):
        
        h,t=dht.read_retry(dht.DHT22,17)
        self.root.ids.lbl_unit_temp.text = str(self.data_mm["unit_temp"])

        if self.data_mm["unit_temp"] == "C":
            self.root.ids.lbl_max_temp.text = str(self.data_mm["max_temp"])
        else:
            self.root.ids.lbl_max_temp.text = str(float(self.data_mm["max_temp"]) + 32)

        if self.data_mm["unit_temp"] == "C":
            self.root.ids.lbl_min_temp.text = str(self.data_mm["min_temp"])
        else:
            self.root.ids.lbl_min_temp.text = str(float(self.data_mm["min_temp"]) + 32)

        self.root.ids.lbl_max_um.text = str(self.data_mm["max_um"])
        self.root.ids.lbl_min_um.text = str(self.data_mm["min_um"])
        
        self.root.ids.knob_temperature._angle=self.calc_angle(t)


    def build(self):
        self.data_mm = {
                        "unit_temp":"C",
                        "max_temp": 0.0,
                        "max_um": 0.0,
                        "min_temp": 0.0,
                        "min_um": 0.0,
                        }

        self.root = Carousel()
        self.start_data()
        event = Clock.schedule_interval(self.my_callback, 5)
        return self.root

    def my_callback(self, dt):
        h,t=dht.read_retry(dht.DHT22,17)
        self.root.ids.knob_temperature._angle=self.calc_angle(t)
        self.root.ids.knob_umidity._angle = (h * 360)/100
        if self.data_mm["unit_temp"] == "C":
            self.root.ids.knob_temperature.value = t
        else:        
            self.root.ids.knob_temperature.value = t + 32

        self.root.ids.knob_umidity.value = h
        with open('./data.json', 'r+') as f:
            data = json.load(f)
            
            if t >float(data["max_temp"]):
                self.data_mm["max_temp"] = "{0:0.1f}".format(t)
                self.update_data_mm()
                f.seek(0)
                json.dump(self.data_mm, f, indent = 4)
                f.truncate()

            elif t < float(data["min_temp"]):
                self.data_mm["min_temp"] = "{0:0.1f}".format(t)
                self.update_data_mm()
                f.seek(0)
                json.dump(self.data_mm, f, indent = 4)
                f.truncate()
            elif h > float(data["max_um"]):
                self.data_mm["max_um"] ="{0:0.1f}".format(h)
                self.update_data_mm()
                f.seek(0)
                json.dump(self.data_mm, f, indent = 4)
                f.truncate()
            elif h < float(data["max_um"]):
                self.data_mm["min_um"] = "{0:0.1f}".format(h)
                self.update_data_mm()
                f.seek(0)
                json.dump(self.data_mm, f, indent = 4)
                f.truncate()
    def reset_mm(self, _obj):
        
        h,t=dht.read_retry(dht.DHT22,17)
        if "um" in _obj.name:
            self.data_mm[_obj.name] = "{0:0.1f}".format(h)
        else:
            self.data_mm[_obj.name] = "{0:0.1f}".format(t)
        
        self.start_data()


    def calc_angle(self, value):
        total_v = 100
        if self.data_mm["unit_temp"] == "C":
            total_v = 100
        else:
            total_v = 150

        if value <= 0:
            absolute_value = value * -1
            return 180 - ((absolute_value * 360)/total_v)
        else:
            return 180 + ((value * 360)/100)


if __name__ == '__main__':
    DemoApp().run()
