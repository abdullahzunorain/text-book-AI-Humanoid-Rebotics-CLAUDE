---
title: "Chapter 1: ROS 2 Architecture"
sidebar_position: 1
---

# Chapter 1: ROS 2 Architecture

ROS 2 (Robot Operating System 2) is the industry-standard middleware framework for building robot software. Despite its name, ROS 2 is not an operating system — it's a collection of libraries, tools, and conventions that help you build modular, distributed robot applications.

## The Computation Graph

At the heart of ROS 2 is the **computation graph** — a network of processes (called **nodes**) that communicate with each other through well-defined interfaces. Think of it as a distributed system where each node handles one responsibility:

- A **camera node** captures images
- A **perception node** detects objects in those images
- A **planning node** decides what to do
- A **motor controller node** sends commands to actuators

These nodes communicate through three mechanisms:

| Mechanism | Pattern | Use Case |
|-----------|---------|----------|
| **Topics** | Publish/Subscribe | Continuous data streams (sensor data, commands) |
| **Services** | Request/Response | One-time queries (get map, set parameter) |
| **Actions** | Goal/Feedback/Result | Long-running tasks (navigate to point, pick up object) |

## DDS: The Middleware Layer

ROS 2 uses the **Data Distribution Service (DDS)** standard as its communication middleware. DDS provides:

- **Automatic discovery**: Nodes find each other without a central broker (unlike ROS 1's `roscore`)
- **Quality of Service (QoS)**: Configure reliability, durability, deadline, and history policies per topic
- **Real-time support**: DDS is used in military, aviation, and industrial systems — it's proven for time-critical applications

The key improvement over ROS 1: **no single point of failure**. In ROS 1, if `roscore` crashed, the entire system went down. ROS 2's DDS discovery is fully distributed.

## Core Concepts

### Packages

A **package** is the unit of organization in ROS 2. Each package contains:
- Source code (Python or C++)
- Launch files
- Configuration files
- A `package.xml` manifest with metadata and dependencies

### Workspaces

A **workspace** is a directory where you build and manage packages:

```
my_ros2_ws/
├── src/               # Source packages go here
│   ├── my_package_1/
│   └── my_package_2/
├── build/             # Build artifacts (auto-generated)
├── install/           # Installed packages (auto-generated)
└── log/               # Build logs (auto-generated)
```

You build with `colcon build` and source with `. install/setup.bash`.

## Code Example: Initializing ROS 2 in Python

Here's the minimal pattern to start a ROS 2 Python node:

```python
import rclpy
from rclpy.node import Node

class MinimalNode(Node):
    def __init__(self):
        super().__init__('minimal_node')
        self.get_logger().info('Hello from ROS 2!')

def main(args=None):
    rclpy.init(args=args)
    node = MinimalNode()

    try:
        rclpy.spin(node)  # Keep the node alive
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Key points:
- `rclpy.init()` initializes the ROS 2 client library
- Every node inherits from `rclpy.node.Node`
- `rclpy.spin()` keeps the node running, processing callbacks
- Always clean up with `destroy_node()` and `rclpy.shutdown()`

## Exercise

**Draw the graph:** Imagine a robot that follows a person. Sketch the computation graph:
1. What nodes would you need? (camera, detector, follower, motor controller?)
2. What topics would connect them?
3. Would you use any services or actions?

*Hint: The camera publishes images, the detector subscribes to images and publishes person positions, the follower subscribes to positions and publishes velocity commands, and the motor controller subscribes to velocity commands.*
