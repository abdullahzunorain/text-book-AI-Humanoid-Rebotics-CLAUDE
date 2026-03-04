---
title: "Chapter 3: Unity Robotics"
sidebar_position: 3
---

# Chapter 3: Unity Robotics

## Learning Objectives

- Understand why Unity is increasingly used for robotics simulation alongside or instead of Gazebo
- Import URDF robot models into Unity using the Unity Robotics Hub package
- Communicate between Unity and ROS 2 using the ROS TCP Connector
- Build a basic simulated robot scene with physics, sensors, and articulation bodies

## Why Unity for Robotics?

Unity is a commercial game engine that has rapidly expanded into robotics simulation, autonomous driving, and synthetic data generation. While Gazebo has been the traditional choice for ROS developers, Unity offers several distinctive advantages:

**Photorealistic rendering** — Unity's Universal Render Pipeline (URP) and High Definition Render Pipeline (HDRP) produce visuals far closer to real-world imagery than Gazebo's OGRE-based renderer. This matters for training vision-based models where domain gap is the primary obstacle to sim-to-real transfer.

**Synthetic data generation** — Unity's Perception package generates labeled datasets (bounding boxes, segmentation masks, depth maps) automatically, eliminating hours of manual annotation.

**Large asset ecosystem** — The Unity Asset Store provides thousands of pre-built environments (warehouses, hospitals, outdoor terrains) that would take months to create from scratch.

**GPU-accelerated physics** — Unity's PhysX engine leverages NVIDIA GPUs for contact-rich simulation, which is critical for grasping and manipulation tasks.

The tradeoff is that Unity is not natively ROS-aware. The **Unity Robotics Hub** bridges this gap with packages for URDF import, ROS communication, and sensor simulation.

### Comparison: Unity vs Gazebo

| Feature | Gazebo | Unity |
|---------|--------|-------|
| Physics engine | ODE/Bullet/DART | PhysX (GPU-accelerated) |
| Rendering quality | Moderate (OGRE) | High (URP/HDRP) |
| ROS 2 integration | Native (ros_gz) | Via ROS TCP Connector |
| Sensor simulation | Plugin-based | Perception package |
| License | Open source (Apache 2.0) | Free for revenue < $100K/year |
| Community | Robotics-focused | Cross-domain (games, XR, sim) |
| Synthetic data | Limited | First-class Perception package |

## Setting Up Unity Robotics Hub

The Unity Robotics Hub provides three core packages for robotics work:

1. **URDF Importer** — converts URDF/XACRO robot descriptions into Unity GameObjects
2. **ROS TCP Connector** — enables bidirectional message passing between Unity and ROS 2
3. **Sensor packages** — camera, LiDAR, and IMU sensor simulations

Install the packages via Unity Package Manager using Git URLs. The following C# editor script verifies that the required packages are available:

```csharp
// Editor/RoboticsHubValidator.cs
// Validates that Unity Robotics Hub packages are installed
using UnityEngine;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;

public class RoboticsHubValidator : EditorWindow
{
    private static ListRequest _listRequest;

    [MenuItem("Robotics/Validate Hub Packages")]
    public static void ValidatePackages()
    {
        _listRequest = Client.List(true);
        EditorApplication.update += CheckProgress;
    }

    private static void CheckProgress()
    {
        if (!_listRequest.IsCompleted) return;
        EditorApplication.update -= CheckProgress;

        string[] required = {
            "com.unity.robotics.ros-tcp-connector",
            "com.unity.robotics.urdf-importer",
        };

        foreach (var pkg in required)
        {
            bool found = false;
            foreach (var installed in _listRequest.Result)
            {
                if (installed.name == pkg)
                {
                    Debug.Log($"[OK] {pkg} v{installed.version}");
                    found = true;
                    break;
                }
            }
            if (!found)
                Debug.LogError($"[MISSING] {pkg} — install via Package Manager");
        }
    }
}
```

## Importing a URDF Robot into Unity

URDF (Unified Robot Description Format) is the standard way to describe robot geometry, joints, and physical properties in ROS. The URDF Importer package converts these descriptions into Unity GameObjects with proper articulation:

```python
# validate_urdf.py — validate URDF structure before Unity import
"""Validate a URDF file has required elements for Unity import."""
import xml.etree.ElementTree as ET
from pathlib import Path


def validate_urdf(urdf_path: str) -> dict:
    """
    Check that a URDF file has the minimum elements needed
    for successful Unity Robotics Hub import.
    """
    tree = ET.parse(urdf_path)
    root = tree.getroot()

    if root.tag != "robot":
        return {"valid": False, "error": "Root element must be <robot>"}

    links = root.findall("link")
    joints = root.findall("joint")

    issues: list[str] = []

    # Check for base_link (required by URDF Importer)
    link_names = [link.attrib.get("name", "") for link in links]
    if "base_link" not in link_names:
        issues.append("Missing 'base_link' — Unity URDF Importer expects it as root")

    # Check that all joints reference existing links
    for joint in joints:
        parent = joint.find("parent")
        child = joint.find("child")
        if parent is not None and parent.attrib.get("link") not in link_names:
            issues.append(f"Joint '{joint.attrib['name']}' parent link not found")
        if child is not None and child.attrib.get("link") not in link_names:
            issues.append(f"Joint '{joint.attrib['name']}' child link not found")

    # Check for visual and collision geometry
    for link in links:
        if link.find("visual") is None:
            issues.append(f"Link '{link.attrib['name']}' has no <visual> element")

    return {
        "valid": len(issues) == 0,
        "robot_name": root.attrib.get("name", "unknown"),
        "num_links": len(links),
        "num_joints": len(joints),
        "link_names": link_names,
        "issues": issues,
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "robot.urdf"
    result = validate_urdf(path)
    print(f"Robot: {result['robot_name']}")
    print(f"Links: {result['num_links']}, Joints: {result['num_joints']}")
    if result["valid"]:
        print("✓ URDF is valid for Unity import")
    else:
        print("✗ Issues found:")
        for issue in result["issues"]:
            print(f"  - {issue}")
```

### Import Steps in Unity

1. Open Unity and go to **Assets → Import Robot from URDF**
2. Select your `.urdf` file — the importer reads all meshes, joints, and physics properties
3. The robot appears as a hierarchy of GameObjects with `ArticulationBody` components
4. Each joint maps to an `ArticulationBody` with the correct joint type (revolute, prismatic, fixed)
5. Colliders and visual meshes are generated automatically from the URDF geometry

The `ArticulationBody` component is Unity's physics representation for robotic chains. Unlike standard `Rigidbody` joints, articulation bodies use Featherstone's algorithm for reduced-coordinate dynamics, providing numerically stable simulation of long kinematic chains like humanoid robots.

## ROS TCP Connector: Unity ↔ ROS 2 Communication

The ROS TCP Connector establishes a TCP socket between Unity and a ROS 2 node. Messages are serialized using ROS message definitions, ensuring type safety:

```python
# ros_tcp_endpoint.py — ROS 2 side of the Unity TCP connection
"""ROS 2 TCP endpoint node for Unity communication."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState


class UnityBridge(Node):
    """Bridges ROS 2 topics to/from Unity via TCP connector."""

    def __init__(self):
        super().__init__("unity_bridge")

        # Subscribe to cmd_vel from Unity
        self.cmd_sub = self.create_subscription(
            Twist, "/unity/cmd_vel", self.cmd_callback, 10
        )

        # Publish joint states to Unity
        self.joint_pub = self.create_publisher(
            JointState, "/unity/joint_states", 10
        )

        self.get_logger().info("Unity bridge node started")
        self.get_logger().info("  Subscribing to: /unity/cmd_vel")
        self.get_logger().info("  Publishing to:  /unity/joint_states")

    def cmd_callback(self, msg: Twist):
        self.get_logger().info(
            f"Received from Unity: linear.x={msg.linear.x:.2f}, "
            f"angular.z={msg.angular.z:.2f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = UnityBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
```

On the Unity side, you configure the TCP connector to point at the ROS 2 machine's IP address (default: `127.0.0.1:10000`). In the Unity Editor, go to **Robotics → ROS Settings** and set the ROS IP address and port. Unity then serializes outgoing messages and deserializes incoming messages using the same format as ROS 2.

## Building a Robot Scene

A complete Unity robot simulation scene typically includes:

1. **Environment** — ground plane, walls, obstacles (use Unity's built-in terrain or Asset Store models)
2. **Robot model** — imported from URDF with ArticulationBody components
3. **Sensors** — Camera, LiDAR, and IMU components attached to the robot
4. **Controller script** — C# MonoBehaviour that reads ROS messages and applies forces/torques

This setup lets you test navigation, manipulation, and perception algorithms in visually rich environments that closely match real-world conditions—a significant advantage over Gazebo's lower-fidelity rendering.

## Key Takeaways

- Unity provides photorealistic rendering and GPU-accelerated physics that help reduce the sim-to-real gap for vision-based robotics
- The Unity Robotics Hub packages (URDF Importer, ROS TCP Connector) bridge the gap between Unity and ROS 2
- URDF robots are imported as ArticulationBody hierarchies that use Featherstone dynamics for stable kinematic chain simulation
- The ROS TCP Connector enables bidirectional ROS 2 message passing, letting you use your existing ROS 2 nodes with Unity scenes
- Unity is particularly strong for synthetic data generation and scenarios requiring high visual fidelity
