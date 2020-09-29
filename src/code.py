import board
import busio
import neopixel
import tools
#import test
import led_driver
import io_controller


class Settings:
    default_settings = {
        "names":{}
    }
    def __init__(self,effect_manager):
        self.effect_manager = effect_manager
        self.group_name = self.effect_manager.io_group.name
        self.tick()
        

    def tick(self):
        self.group_data = self.effect_manager.io_group.pull_group()
        try:
            self.feed_data = self.group_data['feeds']
            self.update_dicts()
        except:
            self.feed_data = None
        
    
           
    def update_dicts(self):
        self.keys = [item['key'] for item in self.feed_data]
        self.names = []
        for name in self.keys: self.names.append(name[len(self.group_name)+1:len(name)])
        self.vals = [item['last_value'] for item in self.feed_data]
        self.ids = [id_num for id_num in range(len(self.keys))]

        #keys
        #ids
        #names
        #vals
        self.key_to_id = dict(zip(self.keys,self.ids))
        self.key_to_name = dict(zip(self.keys,self.names))
        self.key_to_val = dict(zip(self.keys,self.vals))
        self.id_to_key = dict(zip(self.ids,self.keys))
        self.id_to_name = dict(zip(self.ids,self.names))
        self.id_to_val = dict(zip(self.ids,self.vals))
        self.name_to_key = dict(zip(self.names,self.keys))
        self.name_to_id = dict(zip(self.names,self.ids))
        self.name_to_val = dict(zip(self.names,self.vals))
        self.val_to_key = dict(zip(self.vals,self.keys))
        self.val_to_id = dict(zip(self.vals,self.ids))
        self.val_to_name = dict(zip(self.vals,self.names))
        
    
    

class Effect_Manager:
    def __init__(self,drivers, io_group):
        self.drivers = drivers
        self.io_group = io_group
        self.settings = Settings(self)
    def debug_settings(self):
        try:
            for key in self.settings.keys:
                print(self.settings.key_to_val[key])
        except:
            tools.Debug_msg("Error getting settings!",1)
            
        
    def tick(self):
        in_transition = []
        for driver in self.drivers:
            in_transition.append(driver.in_transition)
        if in_transition.count(True)==0:
            self.settings.tick()
            self.set_mode()

    def set_speed(self):
        speed_raw = self.settings.name_to_val['speed']/100
        speed_scale = 1/20
        speed = speed_scale*speed_raw
        print("Speed Raw: {} | Speed Scalled {}".format(speed_raw,speed))
        for driver in self.drivers:
            for segment in driver.segments:
                for pixel in segment.pixels:
                    pixel.color_vel = [speed*4]

    def set_mode(self):
        mode = self.settings.name_to_val['mode']
        if mode == "solid":
            tools.Debug_msg("Setting mode to {}".format("solid"),1)
            hex_color = self.settings.name_to_val['color']
            rgb_color = led_driver.hex_to_rgb(hex_color,len(DRIVER_SETTINGS[0]['color']))
            for driver in self.drivers:
                for segment in driver.segments:
                    segment.in_transition=True
                    for pixel in segment.pixels:
                        pixel.color_target = rgb_color
                        
                        

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



AIRLIFT_GROUP = io_controller.IO_Group("airlift")
DRIVER = led_driver.LED_Driver(DRIVER_SETTINGS,AIRLIFT_GROUP)
EFFECTS = Effect_Manager([DRIVER],AIRLIFT_GROUP)

    



def main():
    EFFECTS.tick()
    for i in range(120):
        DRIVER.tick()
        DRIVER.draw()


while True:
    main()    