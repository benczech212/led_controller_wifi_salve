import board
import busio
import neopixel
import tools
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
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
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2) 
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]
io = IO_HTTP(aio_username, aio_key, wifi)

class IO_Group:
    def __init__(self,name):
        self.name = name
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
