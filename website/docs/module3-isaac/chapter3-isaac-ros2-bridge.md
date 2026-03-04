---
title: "Chapter 3: Isaac ROS 2 Bridge"
sidebar_position: 3
---

# Chapter 3: Isaac ROS 2 Bridge

## Learning Objectives

- Understand how Isaac Sim integrates with ROS 2 through the Isaac ROS Bridge extension
- Publish simulated sensor data from Isaac Sim to ROS 2 topics for autonomous navigation
- Subscribe to ROS 2 commands from planning and control nodes to drive simulated robots
- Set up action graphs in Isaac Sim that automate sensor publishing and joint control

## Isaac Sim and ROS 2: A Native Partnership

While Gazebo's ROS 2 integration relies on an external bridge process that translates between two different messaging systems, Isaac Sim provides a **native ROS 2 bridge** built directly into the simulator as an Omniverse extension. This means ROS 2 messages are published and subscribed from within the simulation process itself, eliminating inter-process serialization overhead and providing tighter timing synchronization.

The Isaac ROS Bridge uses OmniGraph—Isaac Sim's visual programming framework—to wire simulated sensors and actuators to ROS 2 topics. Each sensor or controller is represented as a node in an action graph, and you connect them to ROS 2 publisher or subscriber nodes visually or via Python scripts.

### Architecture

```text
┌──────────────────────────────────┐
│          Isaac Sim Process        │
│  ┌───────────┐  ┌──────────────┐ │
│  │ PhysX 5   │  │ RTX Renderer │ │
│  │ (physics) │  │  (sensors)   │ │
│  └─────┬─────┘  └──────┬───────┘ │
│        │               │          │
│  ┌─────▼───────────────▼───────┐ │
│  │      OmniGraph Pipeline     │ │
│  │  ┌─────────┐ ┌───────────┐  │ │
│  │  │Sensor   │ │ROS 2 Pub/ │  │ │
│  │  │Readout  │→│Subscribe  │  │ │
│  │  └─────────┘ └───────────┘  │ │
│  └──────────────────────────────┘ │
│         │ ROS 2 DDS (in-process) │
└─────────┼────────────────────────┘
          │
    ┌─────▼─────┐
    │  ROS 2    │
    │  Nodes    │
    │ (Nav2,    │
    │  MoveIt2) │
    └───────────┘
```

## Setting Up the ROS 2 Bridge Extension

The ROS 2 bridge comes pre-installed with Isaac Sim. You activate it from the Extensions menu:

1. Open Isaac Sim
2. Go to **Window → Extensions**
3. Search for "ROS 2 Bridge"
4. Enable `omni.isaac.ros2_bridge`

Alternatively, enable it via Python:

```python
# enable_ros2_bridge.py — Enable Isaac ROS 2 bridge via script
"""Configure and validate the Isaac Sim ROS 2 bridge extension."""
from dataclasses import dataclass


@dataclass
class ROS2BridgeConfig:
    """Configuration for the Isaac Sim ROS 2 bridge."""
    extension_name: str = "omni.isaac.ros2_bridge"
    ros_domain_id: int = 0
    qos_reliable: bool = True
    publish_rate_hz: float = 30.0
    use_sim_time: bool = True

    # Topic remapping
    camera_topic: str = "/front_camera/rgb"
    depth_topic: str = "/front_camera/depth"
    lidar_topic: str = "/velodyne/points"
    odom_topic: str = "/odom"
    cmd_vel_topic: str = "/cmd_vel"
    joint_state_topic: str = "/joint_states"
    joint_command_topic: str = "/joint_commands"


def generate_bridge_topics(config: ROS2BridgeConfig) -> list[dict]:
    """Generate the list of ROS 2 topics the bridge will handle.

    Returns a list of dicts describing each bridged topic with
    direction, message type, and publish rate.
    """
    topics = [
        {
            "topic": config.camera_topic,
            "msg_type": "sensor_msgs/msg/Image",
            "direction": "PUBLISH",
            "rate_hz": config.publish_rate_hz,
            "description": "RGB camera image from RTX renderer",
        },
        {
            "topic": config.depth_topic,
            "msg_type": "sensor_msgs/msg/Image",
            "direction": "PUBLISH",
            "rate_hz": config.publish_rate_hz,
            "description": "Depth image from RTX renderer",
        },
        {
            "topic": config.lidar_topic,
            "msg_type": "sensor_msgs/msg/PointCloud2",
            "direction": "PUBLISH",
            "rate_hz": 10.0,
            "description": "3D LiDAR point cloud",
        },
        {
            "topic": config.odom_topic,
            "msg_type": "nav_msgs/msg/Odometry",
            "direction": "PUBLISH",
            "rate_hz": config.publish_rate_hz,
            "description": "Robot odometry from physics engine",
        },
        {
            "topic": config.cmd_vel_topic,
            "msg_type": "geometry_msgs/msg/Twist",
            "direction": "SUBSCRIBE",
            "rate_hz": None,
            "description": "Velocity commands from navigation stack",
        },
        {
            "topic": config.joint_state_topic,
            "msg_type": "sensor_msgs/msg/JointState",
            "direction": "PUBLISH",
            "rate_hz": config.publish_rate_hz,
            "description": "Current joint positions and velocities",
        },
        {
            "topic": config.joint_command_topic,
            "msg_type": "sensor_msgs/msg/JointState",
            "direction": "SUBSCRIBE",
            "rate_hz": None,
            "description": "Joint position/velocity/effort commands",
        },
    ]
    return topics


def print_topic_table(topics: list[dict]) -> None:
    """Print a formatted table of bridge topics."""
    header = f"{'Topic':<35} {'Type':<35} {'Dir':<12} {'Rate':<8}"
    print(header)
    print("-" * len(header))
    for t in topics:
        rate = f"{t['rate_hz']} Hz" if t['rate_hz'] else "event"
        print(f"{t['topic']:<35} {t['msg_type']:<35} {t['direction']:<12} {rate:<8}")


if __name__ == "__main__":
    config = ROS2BridgeConfig(
        ros_domain_id=0,
        publish_rate_hz=30.0,
    )
    topics = generate_bridge_topics(config)
    print(f"ROS 2 Bridge Configuration (Domain ID: {config.ros_domain_id})")
    print(f"Sim time: {config.use_sim_time}, QoS reliable: {config.qos_reliable}\n")
    print_topic_table(topics)
    print(f"\nTotal topics: {len(topics)} "
          f"({sum(1 for t in topics if t['direction'] == 'PUBLISH')} publish, "
          f"{sum(1 for t in topics if t['direction'] == 'SUBSCRIBE')} subscribe)")
    # Expected output:
    #   ROS 2 Bridge Configuration (Domain ID: 0)
    #   Sim time: True, QoS reliable: True
    #
    #   Topic                               Type                                Dir          Rate
    #   (7 topics listed, 5 publish, 2 subscribe)
```

## Action Graphs for Sensor Publishing

OmniGraph action graphs define the data flow from simulated sensors to ROS 2 topics. While you can create them visually in the Isaac Sim UI, scripting them in Python is more reproducible:

```python
# action_graph_builder.py — Build an OmniGraph action graph for ROS 2 publishing
"""Construct an OmniGraph pipeline for Isaac Sim to ROS 2 sensor data flow."""
from dataclasses import dataclass, field


@dataclass
class OmniGraphNode:
    """A single node in an OmniGraph action graph."""
    name: str
    node_type: str
    params: dict = field(default_factory=dict)
    connections_in: list[str] = field(default_factory=list)
    connections_out: list[str] = field(default_factory=list)


def build_camera_publish_graph(
    camera_prim_path: str = "/World/Robot/front_camera",
    topic_name: str = "/front_camera/rgb",
    frame_id: str = "camera_link",
    publish_rate: float = 30.0,
) -> list[OmniGraphNode]:
    """Build OmniGraph nodes for publishing camera images to ROS 2.

    Returns a list of OmniGraphNode objects representing the pipeline:
    OnPlaybackTick → IsaacReadCamera → ROS2CameraHelper → ROS2Publisher
    """
    nodes = [
        OmniGraphNode(
            name="tick",
            node_type="omni.graph.action.OnPlaybackTick",
            connections_out=["camera_reader"],
        ),
        OmniGraphNode(
            name="camera_reader",
            node_type="omni.isaac.sensor.IsaacReadCamera",
            params={
                "cameraPrim": camera_prim_path,
                "renderProductPath": "",
            },
            connections_in=["tick"],
            connections_out=["camera_helper"],
        ),
        OmniGraphNode(
            name="camera_helper",
            node_type="omni.isaac.ros2_bridge.ROS2CameraHelper",
            params={
                "topicName": topic_name,
                "frameId": frame_id,
                "type": "rgb",
            },
            connections_in=["camera_reader"],
            connections_out=["publisher"],
        ),
        OmniGraphNode(
            name="publisher",
            node_type="omni.isaac.ros2_bridge.ROS2Publisher",
            params={
                "publishRate": publish_rate,
                "qosProfile": "RELIABLE",
            },
            connections_in=["camera_helper"],
        ),
    ]
    return nodes


if __name__ == "__main__":
    graph = build_camera_publish_graph(
        camera_prim_path="/World/Carter/front_camera",
        topic_name="/camera/rgb",
    )
    print("Camera publish action graph:")
    for i, node in enumerate(graph):
        arrow = "→" if i < len(graph) - 1 else "■"
        print(f"  [{i+1}] {node.name} ({node.node_type}) {arrow}")
        if node.params:
            for k, v in node.params.items():
                print(f"      {k}: {v}")
    # Expected output:
    #   Camera publish action graph:
    #   [1] tick (omni.graph.action.OnPlaybackTick) →
    #   [2] camera_reader (omni.isaac.sensor.IsaacReadCamera) →
    #       cameraPrim: /World/Carter/front_camera
    #   [3] camera_helper (omni.isaac.ros2_bridge.ROS2CameraHelper) →
    #       topicName: /camera/rgb
    #       frameId: camera_link
    #   [4] publisher (omni.isaac.ros2_bridge.ROS2Publisher) ■
    #       publishRate: 30.0
```

## Connecting Nav2 and MoveIt2

With the ROS 2 bridge active, Isaac Sim becomes a drop-in replacement for a real robot in your autonomy stack:

- **Nav2** subscribes to `/scan` (LiDAR) and `/odom` (odometry), publishes `/cmd_vel` (velocity commands)
- **MoveIt2** subscribes to `/joint_states`, publishes `/joint_commands` for arm manipulation
- **SLAM** (e.g., RTAB-Map) subscribes to RGB-D images and odometry for real-time mapping

The simulation clock published via `/clock` (when `use_sim_time=True`) ensures all ROS 2 nodes stay synchronized with Isaac Sim's physics timestep.

## Performance Considerations

When bridging Isaac Sim with ROS 2, keep these performance tips in mind:

- **Reduce camera resolution** for development—640×480 is sufficient for most testing; save 4K for final validation
- **Lower publish rates** for non-critical topics—LiDAR at 10 Hz, odometry at 30 Hz, camera at 15 Hz
- **Use SHM (shared memory) transport** when Isaac Sim and ROS 2 nodes run on the same machine for zero-copy image transfer
- **Disable rendering** when training with RL—physics-only mode runs 10–100x faster

## Key Takeaways

- Isaac Sim's native ROS 2 bridge runs inside the simulator process, providing tighter synchronization and lower latency than external bridges
- OmniGraph action graphs define the data pipeline from simulated sensors to ROS 2 topics, and can be created visually or scripted in Python
- The bridge supports standard ROS 2 message types, making Isaac Sim a drop-in replacement for real robots with Nav2, MoveIt2, and SLAM stacks
- Simulation time publishing ensures all ROS 2 nodes stay synchronized with the physics engine
- Performance tuning (resolution, publish rate, SHM transport, headless mode) is essential for productive development workflows
