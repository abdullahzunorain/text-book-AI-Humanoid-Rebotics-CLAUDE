---
title: "Chapter 2: Gazebo ROS 2 Integration"
sidebar_position: 2
---

# Chapter 2: Gazebo ROS 2 Integration

## Learning Objectives

- Understand how Gazebo and ROS 2 communicate through the `ros_gz` bridge
- Launch Gazebo simulations from ROS 2 launch files with proper parameter passing
- Subscribe to simulated sensor data (camera, LiDAR, IMU) as standard ROS 2 topics
- Send ROS 2 velocity commands to control simulated robots in Gazebo

## The Bridge Between Simulation and Autonomy

In a real robotics workflow, your perception, planning, and control code runs in ROS 2 while the physical world provides sensor data and accepts actuator commands. The Gazebo–ROS 2 bridge replicates this relationship by translating Gazebo transport messages into ROS 2 topics and vice versa, allowing you to develop and test your entire autonomy stack in simulation before touching real hardware.

The `ros_gz_bridge` package is the official integration layer that performs this message conversion. It can bidirectionally bridge standard message types—`sensor_msgs/Image`, `geometry_msgs/Twist`, `sensor_msgs/LaserScan`, `nav_msgs/Odometry`, and dozens more—with zero custom code. When you deploy to a real robot, you simply swap the bridge for actual sensor drivers while keeping your algorithms unchanged.

### Architecture of ros_gz_bridge

The bridge operates as a ROS 2 node that subscribes to Gazebo transport topics and republishes them as ROS 2 messages (and vice versa). Each mapping is defined by:

1. **Gazebo topic name** — e.g., `/model/robot/cmd_vel`
2. **ROS topic name** — e.g., `/cmd_vel`
3. **Message type pair** — e.g., `gz.msgs.Twist` ↔ `geometry_msgs/msg/Twist`
4. **Direction** — `GZ_TO_ROS`, `ROS_TO_GZ`, or `BIDIRECTIONAL`

You configure these mappings either through command-line arguments or a YAML configuration file.

## Installing the ROS Gazebo Packages

The integration packages are available for ROS 2 Humble and later:

```bash
# Install ros_gz packages for ROS 2 Humble + Gazebo Harmonic
sudo apt-get update
sudo apt-get install -y \
  ros-humble-ros-gz \
  ros-humble-ros-gz-bridge \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-image

# Verify installation
ros2 pkg list | grep ros_gz
# Expected output:
#   ros_gz_bridge
#   ros_gz_image
#   ros_gz_sim
```

These packages provide the bridge node, Gazebo launch integration, and image transport plugins for compressed camera streams.

## Launching Gazebo from a ROS 2 Launch File

Rather than starting Gazebo and ROS 2 separately, you can orchestrate everything from a single ROS 2 launch file. This ensures consistent configuration and simplifies CI/CD automation:

```python
# launch/sim_with_bridge.launch.py
"""ROS 2 launch file: start Gazebo and ros_gz_bridge together."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Declare configurable arguments
    world_arg = DeclareLaunchArgument(
        "world",
        default_value="empty.sdf",
        description="SDF world file to load in Gazebo",
    )

    # Path to ros_gz_sim launch file
    ros_gz_sim_dir = get_package_share_directory("ros_gz_sim")

    # Include Gazebo simulation launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_dir, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": LaunchConfiguration("world")}.items(),
    )

    # Configure the ros_gz_bridge for common topics
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/model/robot/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/model/robot/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/front_camera/image@sensor_msgs/msg/Image@gz.msgs.Image",
            "/lidar/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan",
        ],
        output="screen",
    )

    return LaunchDescription([world_arg, gazebo, bridge])
```

Run this launch file with:

```bash
ros2 launch my_robot_pkg sim_with_bridge.launch.py world:=my_first_world.sdf
```

This single command starts Gazebo with your world, spawns the bridge node, and begins translating messages between the two systems. In your terminal, you can immediately verify the bridged topics:

```bash
ros2 topic list
# Should include:
#   /cmd_vel
#   /model/robot/odometry
#   /front_camera/image
#   /lidar/scan
```

## Controlling a Simulated Robot

Once the bridge is running, controlling a simulated robot is identical to controlling a real one—you publish `geometry_msgs/Twist` messages on the velocity topic:

```python
# teleop_node.py — send velocity commands to a simulated robot via ROS 2
"""Minimal teleop node that publishes Twist messages."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class SimpleTeleop(Node):
    """Publishes constant forward velocity for 5 seconds."""

    def __init__(self):
        super().__init__("simple_teleop")
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.timer = self.create_timer(0.1, self.publish_cmd)  # 10 Hz
        self.elapsed = 0.0
        self.get_logger().info("SimpleTeleop started — driving forward for 5s")

    def publish_cmd(self):
        msg = Twist()
        if self.elapsed < 5.0:
            msg.linear.x = 0.5   # 0.5 m/s forward
            msg.angular.z = 0.1  # slight left turn
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info("Stopping robot")
            self.timer.cancel()

        self.publisher.publish(msg)
        self.elapsed += 0.1


def main(args=None):
    rclpy.init(args=args)
    node = SimpleTeleop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
```

When this node publishes on `/cmd_vel`, the bridge converts the `geometry_msgs/Twist` to `gz.msgs.Twist` and delivers it to the Gazebo model's velocity controller. In the simulator, you will see the robot move forward while turning slightly to the left.

## Reading Simulated Sensor Data

Simulated sensors publish data through Gazebo transport. The bridge makes this data available as standard ROS 2 messages:

```python
# lidar_subscriber.py — subscribe to simulated LiDAR scans
"""Subscribe to bridged LaserScan messages from Gazebo LiDAR."""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LidarListener(Node):
    """Logs statistics from simulated LiDAR scans."""

    def __init__(self):
        super().__init__("lidar_listener")
        self.subscription = self.create_subscription(
            LaserScan, "/lidar/scan", self.scan_callback, 10
        )
        self.get_logger().info("Listening for LiDAR scans on /lidar/scan")

    def scan_callback(self, msg: LaserScan):
        valid_ranges = [r for r in msg.ranges if msg.range_min < r < msg.range_max]
        if valid_ranges:
            min_dist = min(valid_ranges)
            avg_dist = sum(valid_ranges) / len(valid_ranges)
            self.get_logger().info(
                f"Scan: {len(valid_ranges)} valid rays, "
                f"min={min_dist:.2f}m, avg={avg_dist:.2f}m"
            )


def main(args=None):
    rclpy.init(args=args)
    node = LidarListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
```

This subscriber works identically whether the data comes from a simulated LiDAR in Gazebo or a real Velodyne sensor. That portability is the central value of the ROS 2–Gazebo integration.

## Bridge Configuration via YAML

For complex setups with many topics, a YAML configuration file is cleaner than command-line arguments:

```bash
# config/bridge.yaml — YAML-based bridge configuration
# Use with: ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:=bridge.yaml
---
- topic_name: /cmd_vel
  ros_type_name: geometry_msgs/msg/Twist
  gz_type_name: gz.msgs.Twist
  direction: ROS_TO_GZ

- topic_name: /odom
  ros_type_name: nav_msgs/msg/Odometry
  gz_type_name: gz.msgs.Odometry
  direction: GZ_TO_ROS

- topic_name: /camera/image_raw
  ros_type_name: sensor_msgs/msg/Image
  gz_type_name: gz.msgs.Image
  direction: GZ_TO_ROS

- topic_name: /imu/data
  ros_type_name: sensor_msgs/msg/Imu
  gz_type_name: gz.msgs.IMU
  direction: GZ_TO_ROS
```

## Key Takeaways

- The `ros_gz_bridge` package bidirectionally translates between Gazebo and ROS 2 message types, enabling seamless sim-to-real development
- ROS 2 launch files can start Gazebo and the bridge together for reproducible simulation sessions
- Code written against ROS 2 topic interfaces works identically in simulation and on real hardware
- Bridge mappings can be configured via command-line arguments or YAML files depending on complexity
- This integration pattern is the foundation for testing autonomous behaviors, sensor fusion, and navigation algorithms before real-world deployment
