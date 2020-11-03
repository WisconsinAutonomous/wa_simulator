import sys,tty,termios,atexit
from select import select
from pychrono.vehicle import ChDriver
import threading

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

class Controller(ChDriver):
    def __init__(self, vehicle):
        ChDriver.__init__(self, vehicle)

        self.key_getter = KeyGetter()

        self.m_steering_target = 0
        self.m_braking_target = 0
        self.m_throttle_target = 0

        self.m_steering_delta = 0
        self.m_braking_delta = 0
        self.m_throttle_delta = 0

        self.m_throttle_gain = 4.0
        self.m_steering_gain = 4.0
        self.m_braking_gain = 4.0

        self.m_stepsize = 1e-3
    
    def SetStepsize(self, stepsize):
        self.m_stepsize = stepsize

    def SetSteeringDelta(self, steering_delta):
        self.m_steering_delta = steering_delta

    def SetBrakingDelta(self, braking_delta):
        self.m_braking_delta = braking_delta

    def SetThrottleDelta(self, throttle_delta):
        self.m_throttle_delta = throttle_delta
    
    def SetGains(steering_gain, throttle_gain, braking_gain):
        self.m_steering_gain = steering_gain
        self.m_throttle_gain = throttle_gain
        self.m_braking_gain = braking_gain

    def KeyCheck(self):
        try:
            key = self.key_getter()
            if key == -1:
                return
            elif key == 0:
                self.m_throttle_target = ChClamp(self.m_throttle_target + self.m_throttle_delta, 0.0, +1.0);
                if self.m_throttle_target > 0:
                    self.m_braking_target = ChClamp(self.m_braking_target - self.m_braking_delta * 3, 0.0, +1.0);
            elif key == 2:
                self.m_throttle_target = ChClamp(self.m_throttle_target - self.m_throttle_delta * 3, 0.0, +1.0);
                if self.m_throttle_target <= 0:
                    self.m_braking_target = ChClamp(self.m_braking_target + self.m_braking_delta, 0.0, +1.0);
            elif key == 1:
                self.m_steering_target = ChClamp(self.m_steering_target + self.m_steering_delta, -1.0, +1.0)
            elif key == 3:
                self.m_steering_target = ChClamp(self.m_steering_target - self.m_steering_delta, -1.0, +1.0)
            else:
                print("Key not recognized")
                return 0
        except Exception as e:
            print(e)
            return -1
        

    def Advance(self, step):
        # if not self.thread.is_alive():
        #     self.thread.join()
        #     exit(-1)

        self.KeyCheck()

        # Integrate dynamics, taking as many steps as required to reach the value 'step'
        t = 0;
        while t < step:
            h = min(self.m_stepsize, step - t);

            throttle_deriv = self.m_throttle_gain * (self.m_throttle_target - ChDriver.GetThrottle(self));
            steering_deriv = self.m_steering_gain * (self.m_steering_target - ChDriver.GetSteering(self));
            braking_deriv = self.m_braking_gain * (self.m_braking_target - ChDriver.GetBraking(self));

            ChDriver.SetThrottle(self, ChDriver.GetThrottle(self) + h * throttle_deriv);
            ChDriver.SetSteering(self, ChDriver.GetSteering(self) + h * steering_deriv);
            ChDriver.SetBraking(self, ChDriver.GetBraking(self) + h * braking_deriv);

            t += h;