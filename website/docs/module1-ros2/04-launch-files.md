---
title: "Chapter 4: Launch Files"
sidebar_position: 4
---

# Chapter 4: Launch Files

As robot systems grow in complexity, you'll need to start many nodes simultaneously with specific configurations. **Launch files** are the ROS 2 solution — scripts that describe which nodes to start, what parameters to set, and how to wire everything together.

## Why Launch Files?

Consider a mobile robot system that needs:
- A camera driver node
- A LiDAR driver node
- A perception node
- A navigation planner
- A motor controller
- A visualization node

Starting each one manually with `ros2 run` is tedious and error-prone. Launch files let you start all of them with a single command: `ros2 launch my_package my_launch.py`.

## Python Launch Files

ROS 2 supports Python-based launch files (recommended) and XML/YAML formats. Python launch files offer the most flexibility.

### Basic Structure

```python
# File: launch/robot_launch.py

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot_package',
            executable='camera_node',
            name='camera',
            output='screen',
        ),
        Node(
            package='my_robot_package',
            executable='detector_node',
            name='detector',
            output='screen',
            parameters=[{
                'confidence_threshold': 0.8,
                'model_path': '/models/yolo.pt',
            }],
        ),
        Node(
            package='my_robot_package',
            executable='controller_node',
            name='controller',
            output='screen',
            remappings=[
                ('/cmd_vel', '/robot/cmd_vel'),
            ],
        ),
    ])
```

### Key Concepts

| Feature | Description | Example |
|---------|-------------|---------|
| **parameters** | Runtime configuration values | `{'threshold': 0.8}` |
| **remappings** | Redirect topic/service names | `('/cmd_vel', '/robot/cmd_vel')` |
| **output** | Where to send node output | `'screen'` or `'log'` |
| **namespace** | Prefix for all names | `namespace='robot1'` |
| **arguments** | Command-line arguments | `LaunchConfiguration('use_sim')` |

## Code Example: Composable Launch File

Here's a more realistic launch file that uses arguments and conditional logic:

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Declare arguments
    use_sim = DeclareLaunchArgument(
        'use_sim',
        default_value='true',
        description='Use simulation mode'
    )

    robot_name = DeclareLaunchArgument(
        'robot_name',
        default_value='my_robot',
        description='Name of the robot'
    )

    # Nodes
    sensor_node = Node(
        package='my_robot_package',
        executable='sensor_node',
        name='sensor',
        output='screen',
        parameters=[{
            'simulation_mode': LaunchConfiguration('use_sim'),
            'update_rate': 10.0,
        }],
    )

    controller_node = Node(
        package='my_robot_package',
        executable='controller_node',
        name='controller',
        namespace=LaunchConfiguration('robot_name'),
        output='screen',
    )

    # Conditional: only start visualizer if not in sim mode
    visualizer_node = Node(
        condition=IfCondition(LaunchConfiguration('use_sim')),
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
    )

    return LaunchDescription([
        use_sim,
        robot_name,
        sensor_node,
        controller_node,
        visualizer_node,
        LogInfo(msg='Robot system launched!'),
    ])
```

### Running the Launch File

```bash
# Basic launch
ros2 launch my_robot_package robot_launch.py

# With custom arguments
ros2 launch my_robot_package robot_launch.py use_sim:=false robot_name:=robot_alpha

# Show all arguments
ros2 launch my_robot_package robot_launch.py --show-args
```

## Composable Nodes

For performance-critical systems, ROS 2 supports **composable nodes** — multiple nodes running in a single process, sharing memory instead of using IPC:

```python
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

container = ComposableNodeContainer(
    name='my_container',
    namespace='',
    package='rclcpp_components',
    executable='component_container',
    composable_node_descriptions=[
        ComposableNode(
            package='my_package',
            plugin='my_package::CameraNode',
            name='camera',
        ),
        ComposableNode(
            package='my_package',
            plugin='my_package::DetectorNode',
            name='detector',
        ),
    ],
    output='screen',
)
```

This eliminates serialization/deserialization overhead between nodes — critical for high-bandwidth data like images.

## Exercise

**Create a multi-node launch file:**
1. Write a launch file that starts 3 nodes: a publisher, a subscriber, and a logger
2. Add a `use_debug` argument (default `false`) that, when `true`, sets a `log_level` parameter to `DEBUG` on all nodes
3. Add a namespace argument so you can run multiple instances: `ros2 launch my_pkg my_launch.py namespace:=robot1`
4. Test it by launching two instances in separate terminals with different namespaces

*Hint: Use `DeclareLaunchArgument` for the arguments and `LaunchConfiguration` to reference them.*
