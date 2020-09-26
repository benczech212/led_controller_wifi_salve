DEBUG_LVL = 1
class Debug_msg:
    count = 0
    def __init__(self,msg,lvl):
        self.id = Debug_msg.count
        Debug_msg.count+=1
        self.msg = msg
        self.lvl = lvl
        if self.lvl <= DEBUG_LVL:
            self.print()
    def print(self):
        print("[{:>3}] {}".format(self.id,self.msg))

