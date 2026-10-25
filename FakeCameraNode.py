#!/usr/bin/env python3
import math, os

from PIL import Image
from std_msgs.msg import Header
from sensor_msgs.msg import Image as ROSImage, CameraInfo
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, PoseWithCovariance, Twist, TwistWithCovariance, Point, Quaternion, Vector3
from math import tan
import rospy

script_dir = os.path.dirname(os.path.abspath(__file__))

left = Image.open(os.path.join(script_dir, "left.png"))
right = Image.open(os.path.join(script_dir, "right.png"))


class FakeCameraNode:
    def __init__(self):
            self._left_img_pub = rospy.Publisher('left/image_rect', ROSImage, queue_size=10)
            self._left_ci_pub = rospy.Publisher('left/camera_info', CameraInfo, queue_size=10)
            self._right_img_pub = rospy.Publisher('right/image_rect', ROSImage, queue_size=10)
            self._right_ci_pub = rospy.Publisher('right/camera_info', CameraInfo, queue_size=10)
            self._odom_pub = rospy.Publisher('/odom', Odometry, queue_size=10)


    def generate_bogus_message(self):
        time = rospy.Time.now()
        rospy.loginfo(f"Sent message at {time}")
        header_left = Header()
        header_left.stamp = time
        header_left.frame_id = 'left_stereo'

        header_right = Header()
        header_right.stamp =time
        header_right.frame_id = 'right_stereo'

        header_odom = Header()
        header_odom.stamp = time
        header_odom.frame_id = 'odom'



        ROSLeft = ROSImage()

        FOV = math.pi/2


        fx, fy = left.width/tan(FOV/2), left.height/tan(FOV/2)
        cx, cy = left.width/2, left.height/2
        
        ROSLeft.header = header_left
        ROSLeft.width = left.width
        ROSLeft.height = left.height
        ROSLeft.step = left.width * 3
        ROSLeft.encoding='rgb8'
        ROSLeft.is_bigendian=False
        ROSLeft.data = left.tobytes()
        
        self._left_img_pub.publish(ROSLeft)

        ROSRight = ROSImage()


        ROSRight.header = header_right
        ROSRight.width = right.width
        ROSRight.height = right.height
        ROSRight.step = right.width *3
        ROSRight.encoding = 'rgb8'
        ROSRight.is_bigendian = False
        ROSRight.data = right.tobytes()

        self._right_img_pub.publish(ROSRight)

        # published all the images by now

        CILeft = CameraInfo()
        CILeft.height = left.height
        CILeft.header = header_left
        CILeft.width = left.width
        CILeft.distortion_model = 'plumb_bob'
        CILeft.D = [-1, 0, 0, 0, 0] #some bogus parameters for plumb_bob system
        CILeft.K = [fx, 0, cx, 0, fy, cy, 0, 0, 1]
        CILeft.R = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        CILeft.P = [fx, 0, cx, 0, 0, fy, cy, 0, 0, 0, 1, 0]
        self._left_ci_pub.publish(CILeft)

        CIRight = CameraInfo()
        CIRight.header = header_right
        CIRight.height = right.height
        CIRight.width = right.width
        CIRight.distortion_model = 'plumb_bob'
        CIRight.D = [-1, 0, 0, 0, 0]  # some bogus parameters for plumb_bob system
        CIRight.K = [fx, 0, cx, 0, fy, cy, 0, 0, 1]
        CIRight.R = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        CIRight.P = [fx, 0, cx, 0, 0, fy, cy, 0, 0, 0, 1, 0]
        self._right_ci_pub.publish(CIRight)

        # odom message
        odom = Odometry()
        odom.header = header_odom
        odom.child_frame_id='odom'

        pose = Pose()

        position = Point()
        position.x = 0
        position.y = 0
        position.z = 0

        orientation = Quaternion()
        orientation.w = 1
        orientation.x = 0
        orientation.y = 0
        orientation.z = 0


        pose.position = position
        pose.orientation = orientation

        cov_pose = PoseWithCovariance()
        cov_pose.pose = pose
        cov_pose.covariance = [0]*36


        odom.pose =cov_pose

        twist = Twist()
        twist_vec = Vector3()
        twist_vec.x = twist_vec.y = twist_vec.z = 0
        twist.linear = twist_vec
        twist.angular = twist_vec

        cov_twist = TwistWithCovariance()
        cov_twist.twist = twist
        cov_twist.covariance = [0]*36

        odom.twist = cov_twist

        self._odom_pub.publish(odom)

if __name__ == '__main__':
    rospy.init_node('fake_camera')
    node = FakeCameraNode()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        node.generate_bogus_message()
        rate.sleep()

