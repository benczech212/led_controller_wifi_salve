import time
import board
import neopixel

DEBUG_LEVEL = 3


class LED_Driver:
    drivers = []
    count = 0
    def __init__(self,settings,io_group):
        LED_Driver.drivers.append(self)
        self.id = self.count
        LED_Driver.count += 1
        self.segments = []
        for setting in settings:
            self.segments.append(self.init_segment(setting))
        self.brightness = 1.0
        self.is_enabled = True
        self.io_group = io_group
        self.in_transition = False
    def init_segment(self,settings):
        return LED_Segment(self,settings)
    def draw(self):
        if self.is_enabled:
            for segment in self.segments:
                segment.draw()
    def tick(self):
        in_transition = []
        for segment in self.segments:
            segment.tick()
            in_transition.append(segment.in_transition)
        if in_transition.count(True)> 0:
            self.in_transition = True
        else:
            self.in_transition = False


        
        
class LED_Segment:
    def __init__(self,driver,settings):
        self.driver = driver
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
        self.neopixels = self.init_neopixels(self.data_pin,self.pixel_range,self.brightness,self.auto_write,self.pixel_order)
        self.is_enabled = settings['is_enabled']
        self.tick_count = 0
        self.pixels = []
        self.init_pixels()
        self.in_transition = False

    def init_neopixels(self, data_pin, pixel_range, brightness, auto_write, pixel_order):
        return neopixel.NeoPixel(data_pin,pixel_range,brightness=brightness,auto_write=auto_write,pixel_order=pixel_order)

    def init_pixels(self):
        for i in range(self.pixel_range):
            self.pixels.append(Pixel(self,i))

    def tick(self):
        in_transition = []
        for i, pixel in enumerate(self.pixels):
            pixel.tick()
            in_transition.append(pixel.in_transition)
        if in_transition.count(True) > 0:
            self.in_transition = True
        else:
            self.in_transition = False

                    

    def draw(self):
        if self.is_enabled:
            for i, pixel in enumerate(self.pixels):
                color = pixel.get_neopixel_color()
                self.neopixels[i] = color
            self.neopixels.show()
        else:
            self.neopixels.fill(0)
            self.neopixels.show()



class Pixel:
    def __init__(self,segment,px_index):
        self.segment = segment
        self.px_index = px_index
        self.color = [0,0,0,0]
        self.color_exact = [0,0,0,0]
        self.color_target = [0,0,0,0]
        self.color_vel = [4,4,4,4]
        self.in_transition = False
    def tick(self):
        if self.color != self.color_target:
            self.in_transition = True
            self.color_exact = step_to_color(self.color,self.color_target,self.color_vel)
        else: 
            self.in_transition = False

    def get_neopixel_color(self):
        color = []
        for i in self.color_exact:
            color.append(int(i))
        self.color = color
        return tuple(color)


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

def hex_to_rgb(hex_val,channels):
    colors = []
    hex_val = hex_val[1:]
    for i in range(0,6,2):
        val = hex_val[i:i+2]
        val = int(val,16)
        colors.append(val)
    for i in range(abs(len(colors)-channels)):
        colors.append(0)
    return colors

def wheel(pos):
    while pos > 255:
        pos -= 255
    while pos < 255:
        pos += 255

    if pos < 85:
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
