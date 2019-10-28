#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped, Quaternion
import sys
import select
import tty
import termios
import tf

class NonBlockingConsole(object):
    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_data(self):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return False

if __name__ == '__main__':
    try:
        pub = rospy.Publisher('command/pose', PoseStamped, queue_size=10)
        rospy.init_node('pose_publisher', anonymous=True)
        rate = rospy.Rate(50) # 50hz

        pose = PoseStamped()

        pose.header.frame_id = "world"

        pose.pose.position.x = 0
        pose.pose.position.y = 0
        pose.pose.position.z = 1

        yaw = 0.0;
        pitch = 0.0;
        roll = 0.0;

        with NonBlockingConsole() as nbc:
            while not rospy.is_shutdown():
                keyboard_input = nbc.get_data()
                if keyboard_input:
                    if keyboard_input == '8':
                        pose.pose.position.z = pose.pose.position.z  + 0.1
                    elif  keyboard_input == '2':
                        pose.pose.position.z = pose.pose.position.z  -  0.1
                    elif keyboard_input == '4':
                        pose.pose.position.y = pose.pose.position.y  -  0.1
                    elif keyboard_input == '6':
                        pose.pose.position.y = pose.pose.position.y  +  0.1
                    elif keyboard_input == '+':
                        pose.pose.position.x = pose.pose.position.x  +  0.1
                    elif keyboard_input == '-':
                        pose.pose.position.x = pose.pose.position.x  -  0.1
                    elif keyboard_input == '5':
                        yaw = yaw + 0.1
                    else:
                        break

                pose.header.stamp = rospy.Time.now()
                q = tf.transformations.quaternion_from_euler(yaw, pitch, roll, 'rzyx')
                pose.pose.orientation = Quaternion(*q)
                pub.publish(pose)
                rate.sleep()

    except rospy.ROSInterruptException:
        pass
