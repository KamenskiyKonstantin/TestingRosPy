import rospy
from sensor_msgs.msg import PointCloud2
class Receiver:
    def __init__(self):
       self._subscriber = rospy.Subscriber('cloud_obstacles', PointCloud2, self.handle)
    def handle(self, msg: PointCloud2):
        data = msg.data
        step = msg.point_step
        points = [data[i:i+step] for i in range(0, len(data), step)]
        rospy.loginfo(f"fMessage with time {msg.header.stamp} reported f{points}")
