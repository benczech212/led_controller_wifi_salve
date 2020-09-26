import time
import board
import neopixel

DEBUG_LEVEL = 3

SETTINGS = [{"name":"Segment 1",
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
class LED_Driver:
    drivers = []
    count = 0
    def __init__(self):
        LED_Driver.drivers.append(self)
        self.id = self.count
        LED_Driver.count += 1
        self.segments = [self.init_segment(SETTINGS[0])]
        self.brightness = 1.0
        self.is_enabled = True
    def init_segment(self,settings):
        return LED_Segment(self,settings)
    def draw(self):
        if self.is_enabled:
            for segment in self.segments:
                segment.draw()
    def tick(self):
        for segment in self.segments:
            segment.tick()

        
        
class LED_Segment:
    def __init__(self,driver,settings):
        self.driver = driver
        for i in settings: 
            print("{}: {}".format(i, settings[i]))
        self.pixel_min = settings['pixel_min']
        self.pixel_max = settings['pixel_max']
        self.pixel_range = self.pixel_max - self.pixel_min
        self.brightness = settings['brightness']
        self.data_pin = settings['data_pin']
        self.clock_pin = settings['clock_pin']
        self.color_channels = settings['color_channels']
        self.color_channel_multiplier= settings['color_channel_multiplier']
        self.auto_write = settings['auto_write']
        self.pixel_order = settings['pixel_order']
        self.segment = self.init_neopixels(self.data_pin,self.pixel_range,self.brightness,self.auto_write,self.pixel_order)
        self.is_enabled = settings['is_enabled']
        self.tick_count = 0
        self.pixels = []
        self.init_pixels()

    def init_neopixels(self, data_pin, pixel_range, brightness, auto_write, pixel_order):
        return neopixel.NeoPixel(data_pin,pixel_range,brightness=brightness,auto_write=auto_write,pixel_order=pixel_order)

    def init_pixels(self):
        for i in range(self.pixel_range):
            self.pixels.append(Pixel(self,i))

    def tick(self):
        for i, pixel in enumerate(self.pixels):
            pixel.tick()
                    

    def draw(self):
        if self.is_enabled:
            for i, pixel in enumerate(self.pixels):
                color = pixel.get_neopixel_color()
                self.segment[i] = color
            self.segment.show()
        else:
            self.segment.fill(0)
            self.segment.show()
    def test_effect(self):
        for pixel in pixels:
            pixel.color_


class Pixel:
    def __init__(self,segment,px_index):
        self.segment = segment
        self.px_index = px_index
        self.color = [0,0,0,0]
        self.color_target = [0,0,0,0]
        self.color_vel = [4,4,4,4]
    def tick(self):
        if self.color != self.color_target:
            self.color = step_to_color(self.color,self.color_target,self.color_vel)

    def get_neopixel_color(self):
        color = tuple(self.color)
        return color


def debug_msg(msg,lvl):
    if lvl <= DEBUG_LEVEL: print(msg)
        

def step_to_color(color,color_target,color_vel):
    new_color = []
    color_delta = []
    color_target = list(color_target)
    for c in range(len(color)):
        color_val = 0
        color_delta = (color[c] - color_target[c])
        if abs(color_delta) < color_vel[c]:
            color_val = color_target[c]
        elif color_delta > 0:
            color_val=  color[c] - color_vel[c]
        elif color_delta < 0:
            color_val = color[c] + color_vel[c]
        new_color.append(color_val)
    return new_color



def wheel(pos):
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b, 0)



TICK_COUNT = 0
def main_loop():
    global TICK_COUNT
    TICK_COUNT+=1 
    DRIVER.tick()
    DRIVER.draw()
    for i, pixel in enumerate(DRIVER.segments[0].pixels):
        segment_offset = i // pixel.segment.pixel_max
        color_spread = 5
        frame_modifier = TICK_COUNT * 4
        new_hue = (segment_offset * 4) + (color_spread * i) + (frame_modifier)
        new_color = wheel(new_hue)
        pixel.color_target = new_color


DRIVER = LED_Driver()

while __name__ == "__main__":
    main_loop()
