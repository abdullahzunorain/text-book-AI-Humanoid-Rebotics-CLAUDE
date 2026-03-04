---
title: "Chapter 1: Gazebo Basics"
sidebar_position: 1
---

# Chapter 1: Gazebo Basics

## Learning Objectives

- Understand the architecture and core components of the Gazebo simulator
- Learn how to install Gazebo Harmonic and launch your first simulation world
- Create and manipulate basic robot models in a Gazebo environment
- Understand the physics engine, sensor plugins, and world files that drive realistic simulation

## What Is Gazebo?

Gazebo is the de facto open-source 3D robotics simulator used across academia, industry, and competitions worldwide. Originally developed at the University of Southern California and later maintained by Open Robotics, Gazebo provides a physically accurate environment where you can test robot designs, control algorithms, and perception pipelines—all without risking real hardware.

The simulator combines a high-fidelity physics engine (typically ODE, Bullet, DART, or Simbody) with advanced 3D rendering via OGRE, enabling robots to interact with realistic objects under the influence of gravity, friction, and contact dynamics. Gazebo is especially valued in the Physical AI and humanoid robotics community because it supports complex articulated bodies, multi-sensor setups, and large-scale multi-robot scenarios out of the box.

### Why Simulate?

Building physical robots is expensive and time-consuming. A single hardware failure during testing can cost weeks of repair. Simulation lets you:

1. **Iterate faster** — run thousands of test episodes in minutes instead of days.
2. **Test dangerous scenarios** — simulate falls, collisions, and edge cases safely.
3. **Develop in parallel** — software teams can work while hardware is being manufactured.
4. **Reproduce results** — reset the environment deterministically for fair comparisons.

Modern sim-to-real transfer techniques (domain randomization, system identification) have narrowed the gap between simulation and reality, making Gazebo an essential tool in every roboticist's workflow.

## Architecture Overview

Gazebo follows a client–server architecture:

| Component | Role |
|-----------|------|
| **gzserver** | Runs the physics engine, manages models, and publishes simulation state |
| **gzclient** | Provides the 3D visualization window (can be detached or omitted for headless runs) |
| **Transport library** | Protobuf-based messaging between server, client, and plugins |
| **Plugin system** | Extends functionality — sensors, controllers, world events, GUI overlays |

This separation means you can run simulations on a powerful headless server (no GPU needed for physics) and only launch the GUI when you want to inspect results visually.

## Installing Gazebo Harmonic

Gazebo Harmonic is the recommended release for pairing with ROS 2 Humble and later. Install it on Ubuntu 22.04+:

```bash
# Add the OSRF repository
sudo apt-get update
sudo apt-get install -y lsb-release wget gnupg

sudo wget https://packages.osrfoundation.org/gazebo.gpg \
  -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] \
  http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

sudo apt-get update
sudo apt-get install -y gz-harmonic

# Verify installation
gz sim --version
```

After installation, launch the default empty world to verify everything works:

```bash
# Launch Gazebo with the default empty world
gz sim empty.sdf
```

You should see a 3D viewport with a ground plane and sunlight. Close the window or press `Ctrl+C` to shut down the simulation.

## Your First World File

Gazebo worlds are described using **SDF (Simulation Description Format)**, an XML-based language. A minimal world file defines the physics engine, lighting, and ground plane:

```python
# save_world.py — programmatically generate an SDF world file
"""Generate a minimal Gazebo SDF world file."""

WORLD_SDF = """<?xml version="1.0" ?>
<sdf version="1.8">
  <world name="my_first_world">
    <!-- Physics engine configuration -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <!-- Sun light -->
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal></plane></geometry>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
        </visual>
      </link>
    </model>

    <!-- A simple box model -->
    <model name="box">
      <pose>2 0 0.5 0 0 0</pose>
      <link name="link">
        <inertial>
          <mass>1.0</mass>
        </inertial>
        <collision name="collision">
          <geometry><box><size>1 1 1</size></box></geometry>
        </collision>
        <visual name="visual">
          <geometry><box><size>1 1 1</size></box></geometry>
        </visual>
      </link>
    </model>
  </world>
</sdf>
"""

def main():
    output_path = "my_first_world.sdf"
    with open(output_path, "w") as f:
        f.write(WORLD_SDF)
    print(f"World file written to {output_path}")
    print("Launch with: gz sim my_first_world.sdf")

if __name__ == "__main__":
    main()
```

Run this script to create the SDF file, then launch it with `gz sim my_first_world.sdf`. You will see a ground plane with a 1-meter cube floating at a height of 0.5 meters. The box will fall under gravity and settle on the ground—demonstrating the physics engine in action.

## Gazebo Plugins and Sensors

Gazebo's plugin system is what makes it powerful for robotics. Plugins attach to models, links, or the world itself and execute code every simulation step. Common plugin types include:

- **Sensor plugins** — cameras, LiDAR, IMU, GPS, contact sensors
- **Model plugins** — joint controllers, differential drive, custom dynamics
- **World plugins** — object spawning, event triggers, logging

For example, attaching a camera sensor to a robot allows you to test computer vision algorithms in simulation:

```python
# parse_camera_sdf.py — parse camera sensor properties from SDF
"""Parse camera plugin parameters from an SDF model string."""
import xml.etree.ElementTree as ET

CAMERA_SDF = """
<sensor type="camera" name="front_camera">
  <update_rate>30</update_rate>
  <camera>
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
</sensor>
"""

def parse_camera_config(sdf_string: str) -> dict:
    """Extract camera parameters from an SDF sensor element."""
    root = ET.fromstring(sdf_string)
    camera = root.find("camera")
    image = camera.find("image")

    config = {
        "name": root.attrib["name"],
        "type": root.attrib["type"],
        "update_rate": float(root.find("update_rate").text),
        "resolution": (
            int(image.find("width").text),
            int(image.find("height").text),
        ),
        "fov_rad": float(camera.find("horizontal_fov").text),
        "clip_near": float(camera.find("clip/near").text),
        "clip_far": float(camera.find("clip/far").text),
    }
    return config

if __name__ == "__main__":
    config = parse_camera_config(CAMERA_SDF)
    for key, value in config.items():
        print(f"  {key}: {value}")
    # Expected output:
    #   name: front_camera
    #   type: camera
    #   update_rate: 30.0
    #   resolution: (640, 480)
    #   fov_rad: 1.047
    #   clip_near: 0.1
    #   clip_far: 100.0
```

This pattern of defining sensors in SDF and programmatically reading their configuration is common when building perception pipelines that must handle multiple sensor types.

## Physics Engine Tuning

Gazebo supports multiple physics engines, but ODE (Open Dynamics Engine) is the default. Key tuning parameters include:

- **max_step_size** — smaller values give more accurate physics but run slower (default: 0.001 s)
- **real_time_factor** — controls how fast the simulation runs relative to wall-clock time (1.0 = real-time, 0 = as fast as possible)
- **solver iterations** — more iterations improve contact stability at the cost of CPU time

For humanoid robot simulation, where balance and contact dynamics are critical, you typically need at least 50 solver iterations and a step size of 0.001 s or smaller. For wheeled robots, you can often relax these to 20 iterations and 0.005 s for faster training loops.

## Key Takeaways

- Gazebo is the standard open-source 3D simulator for robotics, supporting physics, sensors, and multi-robot scenarios
- Its client–server architecture separates physics computation from visualization, enabling headless and distributed workflows
- SDF (Simulation Description Format) describes worlds, models, and sensors in a declarative XML format
- The plugin system allows extending Gazebo with custom sensors, controllers, and world behaviors
- Physics engine parameters (step size, solver iterations, real-time factor) must be tuned for the specific robot type and use case
