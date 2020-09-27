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


    def read_group(self):
        data = []
        if self.group != None:    
            for feed in self.group['feeds']:
                data.append({feed['key']:feed['last_value']})
        return data

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



airlift_group = IO_Group("airlift")
#DRIVER = led_driver.LED_Driver(DRIVER_SETTINGS)

strip = neopixel.NeoPixel(board.D7,30,brightness=1.0,auto_write=False,pixel_order=neopixel.GRBW)
strip.fill((255,255,255))
strip.show()

    



def main():
        
    
    airlift_group.pull_group()
    data = airlift_group.read_group()
    for i in data:
        for val in i.values():
            for key in i.keys():
                print("{} : {}".format(key,val))
                print("{}".format("-"*20))
    color_target = data.get(airlift_group.name + "."."color")
    color_target.values()
    for segment in DRIVER.segments:
        for pixel in segment.pixels:
            pixel.color_target = color_target
    DRIVER.tick()
    DRIVER.draw()
    for segment in DRIVER.segments:
        segment.segment.fill((255,255,255,255))
        segment.segment.show()

while True:
    main()    