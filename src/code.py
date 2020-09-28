import tools
import led_driver
import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
import neopixel
from adafruit_io.adafruit_io import IO_HTTP
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
try:
    esp32_cs = DigitalInOut(board.ESP_CS)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)
except AttributeError:
    esp32_cs = DigitalInOut(board.D9)
    esp32_ready = DigitalInOut(board.D10)
    esp32_reset = DigitalInOut(board.D5)
##################
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(
    board.NEOPIXEL, 1, brightness=0.2
) 
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]
io = IO_HTTP(aio_username, aio_key, wifi)

class IO_Group:
    def __init__(self,group_name):
        self.name = group_name
        self.feeds = []
        self.group = None
        self.keys = []
        self.dict = []

    def pull_group(self):
        try:
            self.group = io.get_group(self.name)
        except:
            self.error()
            self.group = None
        return self.group

    def error(self):
        error_lvl = 1
        tools.Debug_msg("Error pulling group {}".format(self.name),error_lvl)

    def add_feed(self,feed):
        self.feeds.append({feed.key_name:feed})


    def read_data(self):
        self.data = []
        if self.group != None:    
            for feed in self.group['feeds']:
                self.data.append({"key":feed['key'],"val":feed['last_value']})
        self.keys = [item['key'] for item in self.data]
        self.setting_names = []
        for key in self.keys:
            self.setting_names.append(key[len(self.name)+1:len(key)])
        self.dict = dict(zip(self.keys,self,self.setting_names,self.data))
        return self.data

    def print_setting_names(self):
        for i in self.setting_names:
            tools.Debug_msg("{}".format(i),1)
    def print_data(self):
        for i in self.data:
            tools.Debug_msg("{}: {}".format(i['key'],i['val']),1)

class IO_Feed:
    def __init__(self,group,key_name):
        self.key_name = key_name
        self.full_key = group.name + "." + self.key_name
        self.data = self.pull_data()
        self.feed = self.pull_feed()
        self.next_value = None
        group.add_feed(self)

    def pull_feed(self):
        try:
            self.feed = io.get_feed(self.full_key)
            return self.feed
        except:
            self.error()

    def pull_data(self):
        try:
            self.data = io.receive_data(self.full_key)
            return self.data
        except:
            self.error()

    def push_data(self,data):
        io.send_data(self.full_key, data)

    def error(self):
        tools.Debug_msg("Error pulling feed {}".format(self.full_key),1)
            


    def last_val(self):
        if self.feed['last_value'] == None:
            tools.Debug_msg("Error getting value for {}".format(self.full_key),1)
        else:
            return self.feed['last_value']

class Effect_Manager:
    def __init__(self,drivers, io_group):
        self.drivers = drivers
        self.io_group = io_group

    

    def tick(self):
        pass

    def set_mode(self):
        if mode == "solid":
            for driver in self.drivers:
                for segment in driver.segments:
                    for pixel in segment.pixels:
                        pixel.color_target = self.io_group.dict['']

    def set_power_state(self):
        pass


DRIVER_SETTINGS = [{"name":"Segment 1",
    "pixel_min":0,
    "pixel_max":29,
    "brightness":1.0,
    "data_pin":board.D7,
    "clock_pin":None,
    "color_channels":["Green","Red","Blue","White"],
    "color_channel_multiplier":[1,1,1,1],
    "auto_write":False,
    "pixel_order":neopixel.GRBW,
    "is_enabled":True,
    "color":[0,0,0,0],
    "color_target":[0,0,0,0],
    "color_vel":[1,1,1,1]

    }]



AIRLIFT_GROUP = IO_Group("airlift")
DRIVER = led_driver.LED_Driver(DRIVER_SETTINGS,AIRLIFT_GROUP)
EFFECTS = Effect_Manager([DRIVER],AIRLIFT_GROUP)




    



def main():
    AIRLIFT_GROUP.pull_group()
    AIRLIFT_GROUP.read_data()
    AIRLIFT_GROUP.dict['airlift.brightness']
    DRIVER.tick()
    DRIVER.draw()
    DRIVER

while True:
    main()    