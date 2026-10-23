import math

from PIL import Image
from std_msgs.msg import Header
from sensor_msgs.msg import Image as ROSImage, CameraInfo
from math import tan
import rospy

class FakeCameraNode:
    def __init__(self):
        self._left_img_pub = rospy.Publisher('left/image_rect', ROSImage, queue_size=10)
        self._left_ci_pub = rospy.Publisher('left/camera_info', CameraInfo, queue_size=10)
        self._right_img_pub = rospy.Publisher('right/image_rect', ROSImage, queue_size=10)
        self._right_ci_pub = rospy.Publisher('right/camera_info', CameraInfo, queue_size=10)


    def generate_bogus_message(self):
        time = rospy.Time.now()
        rospy.loginfo(f"Sent message at {time}")
        header_left = Header()
        header_left.stamp = time

        header_left.frame_id = 'left_stereo'
        header_right = Header()
        header_right.stamp =time
        header_right.frame_id = 'right_stereo'

        ROSLeft = ROSImage()

        FOV = math.pi/2


        left = Image.open('left.png')

        fx, fy = left.width/tan(FOV/2), left.height/tan(FOV/2)
        cx, cy = left.width, left.height
        
        ROSLeft.header = header_left
        ROSLeft.width = left.width
        ROSLeft.height = left.height
        ROSLeft.step = left.width*3
        ROSLeft.encoding='rgb8'
        ROSLeft.is_bigendian=False
        ROSLeft.data = left.tobytes()
        
        self._left_img_pub.publish(ROSLeft)

        ROSRight = ROSImage()

        right = Image.open('right.png')

        ROSRight.header = header_right
        ROSRight.width = right.width
        ROSRight.height = right.height
        ROSRight.step = right.width * 3
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

if __name__ == '__main__':
    rospy.init_node('fake_camera')
    node = FakeCameraNode()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        node.generate_bogus_message()
        rate.sleep()

