# WA Simulator
from wa_simulator.controller.controller import WAController

# Other imports
import sys,tty,termios,atexit
from select import select
import threading
from math import ceil

class KeyGetter:
    def __init__(self):
        # Save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        # New terminal setting unbuffered
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        # Support normal-terminal reset at exit
        atexit.register(self.set_normal_term)
        
    def __call__(self):
        dr,dw,de = select([sys.stdin], [], [], 0)
        if dr == []:
            return -1

        c = sys.stdin.read(3)[2]
        vals = [65, 67, 66, 68]

        if (vals.count(ord(c)) == 0):
            print(f"{ord(c)} is not an arrow key.")
            self.set_normal_term()
            exit(0)

        return vals.index(ord(c))

    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

def ChClamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)

class WAKeyboardController():
    def __init__(self, sys):
        self.key_getter = KeyGetter()

        self.steering_target = 0
        self.braking_target = 0
        self.throttle_target = 0

        self.steering_delta = ceil(sys.GetRenderStepSize() / 1.0)
        self.throttle_delta = ceil(sys.GetRenderStepSize() / 1.0)
        self.braking_delta = ceil(sys.GetRenderStepSize() / 0.3)

        self.throttle_gain = 4.0
        self.steering_gain = 4.0
        self.braking_gain = 4.0

        self.steering = 0
        self.throttle = 0
        self.braking = 0

    def SetSteeringDelta(self, steering_delta):
        self.steering_delta = steering_delta

    def SetBrakingDelta(self, braking_delta):
        self.braking_delta = braking_delta

    def SetThrottleDelta(self, throttle_delta):
        self.throttle_delta = throttle_delta
    
    def SetGains(steering_gain, throttle_gain, braking_gain):
        self.steering_gain = steering_gain
        self.throttle_gain = throttle_gain
        self.braking_gain = braking_gain

    def KeyCheck(self):
        try:
            key = self.key_getter()
            if key == -1:
                return
            elif key == 0:
                self.throttle_target = ChClamp(self.throttle_target + self.throttle_delta, 0.0, +1.0);
                if self.throttle_target > 0:
                    self.braking_target = ChClamp(self.braking_target - self.braking_delta * 3, 0.0, +1.0);
            elif key == 2:
                self.throttle_target = ChClamp(self.throttle_target - self.throttle_delta * 3, 0.0, +1.0);
                if self.throttle_target <= 0:
                    self.braking_target = ChClamp(self.braking_target + self.braking_delta, 0.0, +1.0);
            elif key == 1:
                self.steering_target = ChClamp(self.steering_target + self.steering_delta, -1.0, +1.0)
            elif key == 3:
                self.steering_target = ChClamp(self.steering_target - self.steering_delta, -1.0, +1.0)
            else:
                print("Key not recognized")
                return 0
        except Exception as e:
            print(e)
            return -1
        

    def Advance(self, step):
        self.KeyCheck()

        # Integrate dynamics, taking as many steps as required to reach the value 'step'
        t = 0;
        while t < step:
            h = step - t

            steering_deriv = self.steering_gain * (self.steering_target - self.steering)
            throttle_deriv = self.throttle_gain * (self.throttle_target - self.throttle)
            braking_deriv = self.braking_gain * (self.braking_target - self.braking)

            self.steering += h * steering_deriv
            self.throttle += h * throttle_deriv
            self.braking += h * braking_deriv

            t += h

    def Synchronize(self, time):
        pass
    
    def GetInputs(self):
        return {"steering": self.steering, "throttle": self.throttle, "braking": self.braking}
