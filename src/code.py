import tools
#import led_driver
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
    def add_feed(self,feed):
        self.feeds.append({feed.key_name:feed})

class IO_Feed:
    def __init__(self,group,key_name):
        self.key_name = key_name
        self.full_key = group.name + "." + self.key_name
        self.feed = None
        group.add_feed(self)

    def pull(self):
        try:
            self.feed = io.get_feed(self.full_key)
            return self.feed
        except:
            self.error()
    def pull_val(self):
        try:
            self.feed = io.get_feed("airlift.power-state")
            #self.feed = io.get_feed(self.full_key)
            return self.get_val()
        except:
            self.error()    
    def error(self):
        tools.Debug_msg("Error pulling feed {}".format(self.full_key),1)
            
    def get_val(self):
        return self.feed['last_value']


def setup_io():
    airlift_group = IO_Group("airlift")
    power_state = IO_Feed(airlift_group,"power-state")
    color = IO_Feed(airlift_group,"color")
    speed = IO_Feed(airlift_group,"speed")
    return airlift_group


#specified_feed = io.get_feed("circuitpython")
#print(specified_feed['last_value'])

AIRLIFT = setup_io()
while True:
    for feed in AIRLIFT.feeds:
        power_state= feed.get('power-state')
        print(power_state.pull_val)
        
   