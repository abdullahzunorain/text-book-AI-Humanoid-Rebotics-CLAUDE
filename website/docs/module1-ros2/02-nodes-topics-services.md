---
title: "Chapter 2: Nodes, Topics & Services"
sidebar_position: 2
---

# Chapter 2: Nodes, Topics & Services

In this chapter, we dive into the three core communication patterns of ROS 2: **topics** (publish/subscribe), **services** (request/response), and practical patterns for building node networks.

## Topics: Publish/Subscribe

Topics are **named channels** for continuous, asynchronous data flow. A publisher sends messages to a topic; any number of subscribers can listen.

### Key Properties of Topics

- **Decoupled**: Publishers don't know (or care) who subscribes
- **Many-to-many**: Multiple publishers can write to the same topic; multiple subscribers can read
- **Typed**: Every topic has a fixed message type (e.g., `sensor_msgs/msg/Image`)
- **Asynchronous**: Publishers and subscribers run independently

### Common Message Types

| Message Type | Package | Fields | Use |
|-------------|---------|--------|-----|
| `String` | `std_msgs` | `data: string` | Debug output, simple text |
| `Twist` | `geometry_msgs` | `linear: Vector3, angular: Vector3` | Velocity commands |
| `Image` | `sensor_msgs` | `data: uint8[], width, height, encoding` | Camera images |
| `LaserScan` | `sensor_msgs` | `ranges: float[], angle_min, angle_max` | LiDAR data |
| `Odometry` | `nav_msgs` | `pose, twist` | Robot position + velocity |

## Code Example: Minimal Publisher

Here's a complete publisher node that sends messages every second:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS 2! Message #{self.count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = MinimalPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### How It Works

1. `create_publisher(String, 'chatter', 10)` — creates a publisher of type `String` on topic `chatter` with a queue depth of 10
2. `create_timer(1.0, callback)` — calls `timer_callback` every 1 second
3. `publisher_.publish(msg)` — sends the message to all subscribers on `chatter`

## Services: Request/Response

Services are for **synchronous, one-shot interactions**. A client sends a request; the server processes it and sends a response.

### When to Use Services vs Topics

| Use Topics When... | Use Services When... |
|--------------------|---------------------|
| Data flows continuously | You need a one-time answer |
| Multiple consumers need the data | Only one node should respond |
| Timing doesn't matter | You need a guaranteed response |
| Sensor streams, velocity commands | Map queries, parameter changes |

### Service Structure

Every service has a **request** message and a **response** message:

```
# Example: AddTwoInts.srv
int64 a
int64 b
---
int64 sum
```

The `---` separates request fields from response fields.

## Quality of Service (QoS)

QoS profiles let you tune topic behavior:

- **Reliable**: Guarantees message delivery (retransmits if lost) — use for commands
- **Best Effort**: No retransmission; lower latency — use for high-frequency sensor data
- **Transient Local**: New subscribers receive the last published message — use for maps, configurations

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy

qos = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.BEST_EFFORT
)
self.create_subscription(LaserScan, '/scan', self.callback, qos)
```

## Exercise

**Build a subscriber:** Write a subscriber node that:
1. Subscribes to the `chatter` topic (type `std_msgs/msg/String`)
2. Logs every received message with `self.get_logger().info(...)`
3. Counts the total messages received and logs the count every 10 messages

*Hint: Use `self.create_subscription(String, 'chatter', self.callback, 10)` and keep a counter as an instance variable.*
