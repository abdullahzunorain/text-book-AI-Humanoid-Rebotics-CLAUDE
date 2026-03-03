---
title: "Chapter 3: Python Packages"
sidebar_position: 3
---

# Chapter 3: Python Packages

In ROS 2, all code is organized into **packages** — self-contained units with their own dependencies, entry points, and metadata. This chapter covers how to create, structure, and build Python packages.

## Package Structure

A standard ROS 2 Python package looks like this:

```
my_robot_package/
├── package.xml              # Package manifest (name, version, deps)
├── setup.py                 # Python package setup
├── setup.cfg                # Tool configuration
├── resource/
│   └── my_robot_package     # Marker file for ament index
├── my_robot_package/
│   ├── __init__.py
│   ├── my_node.py           # Your node implementation
│   └── utils.py             # Helper modules
├── launch/
│   └── my_launch.py         # Launch files
├── config/
│   └── params.yaml          # Parameter files
└── test/
    ├── test_copyright.py
    ├── test_flake8.py
    └── test_pep257.py
```

## Creating a Package

Use the `ros2 pkg create` command:

```bash
cd ~/my_ros2_ws/src

# Create a Python package with a node
ros2 pkg create --build-type ament_python \
    --node-name my_node \
    my_robot_package

# This generates the full package structure above
```

### Key Files Explained

**`package.xml`** — The manifest file:
```xml
<?xml version="1.0"?>
<package format="3">
  <name>my_robot_package</name>
  <version>0.0.1</version>
  <description>My robot control package</description>
  <maintainer email="dev@example.com">Developer</maintainer>
  <license>MIT</license>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

**`setup.py`** — Entry points that register your nodes as executables:
```python
from setuptools import find_packages, setup

package_name = 'my_robot_package'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['launch/my_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'my_node = my_robot_package.my_node:main',
        ],
    },
)
```

## Code Example: Complete Package Creation

Here's the full workflow to create and run a package:

```python
# File: my_robot_package/my_robot_package/my_node.py

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocityCommander(Node):
    """Publishes velocity commands to move a robot forward."""

    def __init__(self):
        super().__init__('velocity_commander')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.5, self.publish_velocity)
        self.get_logger().info('Velocity Commander started!')

    def publish_velocity(self):
        msg = Twist()
        msg.linear.x = 0.5   # Forward at 0.5 m/s
        msg.angular.z = 0.0   # No rotation
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = VelocityCommander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

### Build and Run

```bash
# Build the workspace
cd ~/my_ros2_ws
colcon build --packages-select my_robot_package

# Source the workspace
source install/setup.bash

# Run the node
ros2 run my_robot_package my_node
```

## Dependency Management

### Types of Dependencies

| Tag in package.xml | When Needed | Example |
|--------------------|----|---------|
| `<depend>` | Build + runtime | `rclpy`, `std_msgs` |
| `<build_depend>` | Build only | `rosidl_default_generators` |
| `<exec_depend>` | Runtime only | `ros2launch` |
| `<test_depend>` | Testing only | `ament_flake8` |

### Installing Dependencies

```bash
# Install all deps for packages in workspace
cd ~/my_ros2_ws
rosdep install --from-paths src --ignore-src -r -y
```

## Exercise

**Create your own package:**
1. Create a package called `sensor_reader` with `ament_python` build type
2. Add a node called `imu_publisher` that publishes simulated IMU data to `/imu/data` topic
3. Use message type `sensor_msgs/msg/Imu`
4. Publish at 10 Hz (timer period = 0.1 seconds)
5. Build, source, and verify it works with `ros2 topic echo /imu/data`

*Hint: Look at the `sensor_msgs/msg/Imu` message definition with `ros2 interface show sensor_msgs/msg/Imu`.*
