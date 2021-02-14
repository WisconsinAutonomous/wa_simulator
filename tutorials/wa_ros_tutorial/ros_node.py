import rclpy
from rclpy.node import Node

from std_msgs.msg import String
import numpy as np
import time

class WASimulatorControlNode(Node):

    def __init__(self):
        super().__init__('wa_simulator_control_node')
        self.publisher = self.create_publisher(String, '/wa_simulator/control', 1)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = f"{np.sin(time.time())},0.1,0.0"
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    control_node = WASimulatorControlNode()

    rclpy.spin(control_node)


    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()