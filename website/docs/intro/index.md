---
title: "Introduction: What is Physical AI?"
sidebar_position: 1
---

# Introduction: What is Physical AI?

Physical AI is the branch of artificial intelligence focused on embodied agents — robots and autonomous systems that interact with the physical world through sensors, actuators, and real-time computation. Unlike purely digital AI (chatbots, recommendation systems), Physical AI must deal with the messy reality of physics: friction, latency, sensor noise, and unpredictable environments.

## Why Physical AI Matters

The next wave of AI isn't just about language models and image generators. It's about intelligent machines that can:

- **Navigate** warehouses, hospitals, and disaster zones
- **Manipulate** objects with dexterous humanoid hands
- **Collaborate** with humans in shared workspaces
- **Adapt** to changing environments in real time

Companies like Boston Dynamics, Tesla (Optimus), Figure AI, and Agility Robotics are racing to build general-purpose humanoid robots. The global humanoid robotics market is projected to reach $38 billion by 2035.

## Sensor Systems Overview

Physical AI relies on a rich sensory pipeline. Here are the primary sensor modalities:

| Sensor Type | What It Measures | Example |
|------------|-----------------|---------|
| **LiDAR** | 3D point clouds (distance) | Velodyne VLP-16 |
| **Camera (RGB)** | Color images | Intel RealSense D435 |
| **Depth Camera** | RGB + depth per pixel | Azure Kinect DK |
| **IMU** | Acceleration + angular velocity | MPU-6050 |
| **Force/Torque** | Contact forces | ATI Mini45 |
| **Encoders** | Joint positions | Incremental rotary encoder |

## Code Example: Reading Sensor Data

Here's a simple Python example that reads simulated IMU data — the kind of pattern you'll use throughout this textbook:

```python
import time
import random

class IMUSensor:
    """Simulated IMU sensor for learning purposes."""

    def read(self) -> dict:
        """Return simulated accelerometer + gyroscope data."""
        return {
            "accel_x": random.gauss(0, 0.1),
            "accel_y": random.gauss(0, 0.1),
            "accel_z": random.gauss(9.81, 0.1),  # Gravity
            "gyro_x": random.gauss(0, 0.01),
            "gyro_y": random.gauss(0, 0.01),
            "gyro_z": random.gauss(0, 0.01),
            "timestamp": time.time(),
        }

# Usage
sensor = IMUSensor()
for i in range(5):
    reading = sensor.read()
    print(f"Reading {i+1}: accel_z={reading['accel_z']:.2f} m/s²")
    time.sleep(0.1)
```

This pattern — **initialize a sensor, read data in a loop, process it** — is the foundation of every robotics system.

## What You'll Learn in This Textbook

This textbook covers the essential building blocks of Physical AI:

1. **Introduction** (this chapter): What Physical AI is and why it matters
2. **Module 1: ROS 2 Fundamentals**: The Robot Operating System — the industry-standard framework for building robot software

By the end, you'll understand how to structure robot software, communicate between components, and describe robot hardware — all skills needed to build real Physical AI systems.

## Exercise

**Think about it:** Name three everyday devices that use Physical AI principles (sensors + computation + physical action). For each, identify:
- What sensors does it use?
- What decisions does it make?
- What physical actions does it take?

*Examples: a Roomba vacuum, a self-driving car, a drone delivery system.*
