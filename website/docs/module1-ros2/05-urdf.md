---
title: "Chapter 5: URDF — Robot Description"
sidebar_position: 5
---

# Chapter 5: URDF — Robot Description

The **Unified Robot Description Format (URDF)** is an XML-based file format for describing a robot's physical structure. URDF defines the robot's links (rigid bodies), joints (connections between links), and visual/collision properties. It's the standard way to tell ROS 2 what your robot looks like and how it moves.

## Why URDF?

Every robotics tool in the ROS 2 ecosystem needs to know the robot's structure:
- **RViz** needs URDF to visualize the robot
- **MoveIt** needs URDF to plan collision-free motions
- **Gazebo** needs URDF (converted to SDF) to simulate physics
- **TF2** needs URDF to compute coordinate transforms between frames

Without URDF, these tools don't know where the robot's arms are, how its wheels connect, or what it looks like.

## Links and Joints

### Links

A **link** is a rigid body with three optional properties:

| Property | Purpose | Example |
|----------|---------|---------|
| **visual** | What it looks like in RViz | Mesh file, cylinder, box |
| **collision** | Simplified shape for collision detection | Usually a simpler geometry than visual |
| **inertial** | Mass and inertia tensor for physics simulation | Required for Gazebo |

### Joints

A **joint** connects two links and defines how they move relative to each other:

| Joint Type | Motion | Example |
|-----------|--------|---------|
| **fixed** | No motion | Sensor mounted on chassis |
| **revolute** | Rotation with limits | Arm joint (elbow) |
| **continuous** | Unlimited rotation | Wheel |
| **prismatic** | Linear sliding | Elevator, linear actuator |

### The Parent-Child Tree

URDF forms a **tree structure**: every link has exactly one parent joint (except the root link). This means:

```
base_link (root)
├── base_to_wheel_left (continuous joint)
│   └── wheel_left
├── base_to_wheel_right (continuous joint)
│   └── wheel_right
└── base_to_lidar (fixed joint)
    └── lidar_link
```

## Code Example: Simple Two-Wheeled Robot

Here's a complete URDF for a simple differential-drive robot:

```xml
<?xml version="1.0"?>
<robot name="simple_bot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Base Link (chassis) -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0.0 0.0 0.8 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0"
               iyy="0.02" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Left Wheel -->
  <link name="wheel_left">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.02"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.02"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0" ixz="0"
               iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Left Wheel Joint -->
  <joint name="base_to_wheel_left" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_left"/>
    <origin xyz="0.0 0.12 -0.05" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Right Wheel -->
  <link name="wheel_right">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.02"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.02"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0" ixz="0"
               iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Right Wheel Joint -->
  <joint name="base_to_wheel_right" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_right"/>
    <origin xyz="0.0 -0.12 -0.05" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- LiDAR Sensor -->
  <link name="lidar_link">
    <visual>
      <geometry>
        <cylinder radius="0.03" length="0.04"/>
      </geometry>
      <material name="red">
        <color rgba="0.8 0.0 0.0 1.0"/>
      </material>
    </visual>
  </link>

  <!-- LiDAR Joint (fixed to chassis) -->
  <joint name="base_to_lidar" type="fixed">
    <parent link="base_link"/>
    <child link="lidar_link"/>
    <origin xyz="0.1 0 0.07"/>
  </joint>

</robot>
```

### What Each Part Does

- **`<link>`** defines a physical body with visual appearance, collision shape, and mass
- **`<joint>`** connects two links with `<parent>` and `<child>` tags
- **`<origin>`** sets position (`xyz`) and orientation (`rpy` = roll-pitch-yaw) of the joint
- **`<axis>`** defines the axis of rotation/translation for the joint
- **Material colors** are defined inline with `<material>` and RGBA values

## Visualizing URDF in RViz

To see your robot in RViz:

```bash
# Install the joint state publisher GUI
sudo apt install ros-humble-joint-state-publisher-gui

# Launch visualization
ros2 launch urdf_tutorial display.launch.py model:=path/to/simple_bot.urdf
```

RViz will show the robot, and the Joint State Publisher GUI will let you drag sliders to move the joints.

## Xacro: URDF Macros

Real robots have repetitive structures (two identical wheels, four identical legs). **Xacro** (XML macros) lets you define reusable components:

```xml
<xacro:macro name="wheel" params="name x_pos y_pos">
  <link name="${name}">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.02"/>
      </geometry>
    </visual>
  </link>
  <joint name="base_to_${name}" type="continuous">
    <parent link="base_link"/>
    <child link="${name}"/>
    <origin xyz="${x_pos} ${y_pos} -0.05" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>
</xacro:macro>

<!-- Use the macro -->
<xacro:wheel name="wheel_left" x_pos="0.0" y_pos="0.12"/>
<xacro:wheel name="wheel_right" x_pos="0.0" y_pos="-0.12"/>
```

Process xacro into URDF: `xacro simple_bot.urdf.xacro > simple_bot.urdf`

## Exercise

**Design a robot arm URDF:**
1. Create a URDF for a 3-DOF (degree of freedom) robot arm
2. It should have: `base_link` → `shoulder_link` (revolute) → `upper_arm_link` (revolute) → `forearm_link` (revolute)
3. Make the links different colors so you can distinguish them in RViz
4. Add appropriate `<limit>` tags to constrain joint angles (e.g., shoulder: -90° to 90°)
5. Bonus: Convert to xacro with a reusable `arm_joint` macro

*Hint: For revolute joints, add `<limit lower="-1.5708" upper="1.5708" effort="10" velocity="1.0"/>` inside the `<joint>` tag.*
