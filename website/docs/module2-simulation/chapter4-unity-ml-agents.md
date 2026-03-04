---
title: "Chapter 4: Unity ML-Agents"
sidebar_position: 4
---

# Chapter 4: Unity ML-Agents

## Learning Objectives

- Understand the Unity ML-Agents Toolkit architecture and how it integrates with reinforcement learning frameworks
- Set up a training environment for a robotic agent using ML-Agents observations, actions, and rewards
- Train a simulated robot to perform locomotion and manipulation tasks using PPO (Proximal Policy Optimization)
- Export trained policies and evaluate agent performance using TensorBoard

## What Is Unity ML-Agents?

The Unity ML-Agents Toolkit is an open-source project that enables games and simulations built in Unity to serve as environments for training intelligent agents via deep reinforcement learning (RL), imitation learning, and neuroevolution. For robotics, this means you can train robot control policies—locomotion, grasping, navigation—entirely in simulation before deploying to physical hardware.

ML-Agents bridges Unity (C#) and Python-based ML frameworks (PyTorch) through a communication layer. The architecture consists of three main components:

1. **Learning Environment (Unity)** — the simulation scene where agents observe, act, and receive rewards
2. **Python Trainer** — the `mlagents-learn` CLI tool that runs PPO, SAC, or GAIL training algorithms
3. **Communicator** — a gRPC channel connecting Unity and Python for exchanging observations and actions

This separation lets roboticists use familiar Python-based RL research code while leveraging Unity's high-performance physics and rendering for environment simulation.

### Why ML-Agents for Robotics?

Traditional robotics control uses hand-crafted PID controllers or model-based planners. These work well for structured tasks but struggle with:

- **High-dimensional action spaces** — humanoid robots with 20+ joints
- **Unstructured environments** — cluttered floors, varying lighting, unexpected obstacles
- **Contact-rich manipulation** — grasping deformable objects, tool use

Reinforcement learning addresses these challenges by discovering optimal control policies through trial and error—and ML-Agents makes this accessible with GPU-accelerated parallel environments.

## Setting Up a Training Environment

An ML-Agents training environment requires three C# components attached to a Unity GameObject:

1. **Agent** — makes decisions, receives rewards
2. **Behavior Parameters** — defines observation/action shapes
3. **Decision Requester** — controls decision frequency

Here's a configuration script that sets up a robot reaching task:

```python
# ml_agents_config.py — Generate ML-Agents training configuration YAML
"""Generate a training configuration file for ML-Agents PPO."""

import yaml
from pathlib import Path


def generate_training_config(
    behavior_name: str = "RobotReacher",
    max_steps: int = 500_000,
    learning_rate: float = 3e-4,
    batch_size: int = 1024,
    buffer_size: int = 10240,
    num_layers: int = 2,
    hidden_units: int = 256,
    num_epochs: int = 3,
    gamma: float = 0.99,
) -> dict:
    """Build a PPO training configuration dictionary.

    Returns a config dict compatible with mlagents-learn YAML format.
    """
    config = {
        "behaviors": {
            behavior_name: {
                "trainer_type": "ppo",
                "hyperparameters": {
                    "batch_size": batch_size,
                    "buffer_size": buffer_size,
                    "learning_rate": learning_rate,
                    "beta": 5e-3,        # Entropy regularization
                    "epsilon": 0.2,      # PPO clipping parameter
                    "lambd": 0.95,       # GAE lambda
                    "num_epoch": num_epochs,
                    "learning_rate_schedule": "linear",
                },
                "network_settings": {
                    "normalize": True,
                    "hidden_units": hidden_units,
                    "num_layers": num_layers,
                    "vis_encode_type": "simple",
                },
                "reward_signals": {
                    "extrinsic": {
                        "gamma": gamma,
                        "strength": 1.0,
                    }
                },
                "max_steps": max_steps,
                "time_horizon": 64,
                "summary_freq": 10000,
            }
        }
    }
    return config


def save_config(config: dict, output_path: str = "config/robot_training.yaml"):
    """Write training config to a YAML file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    print(f"Training config saved to {output_path}")
    return output_path


if __name__ == "__main__":
    config = generate_training_config(
        behavior_name="HumanoidWalker",
        max_steps=2_000_000,
        hidden_units=512,
        num_layers=3,
    )
    path = save_config(config)
    print(f"\nTo train, run:")
    print(f"  mlagents-learn {path} --run-id=humanoid_v1")
    # Expected output:
    #   Training config saved to config/robot_training.yaml
    #   To train, run:
    #     mlagents-learn config/robot_training.yaml --run-id=humanoid_v1
```

## Training Loop: Observations, Actions, and Rewards

The RL training loop in ML-Agents follows the standard Markov Decision Process (MDP) cycle:

1. **Observe** — the agent reads its current state (joint positions, velocities, sensor readings)
2. **Decide** — the neural network policy maps observations to actions
3. **Act** — actions are applied to the robot (joint torques, target positions)
4. **Reward** — a scalar reward signal tells the agent how well it performed
5. **Learn** — PPO updates the policy based on collected experience

The reward function is the most critical design decision. For a reaching task, you might use:

```python
# reward_calculator.py — Compute rewards for a robot reaching task
"""Reward function for a robotic arm reaching a target position."""
import math


def compute_reaching_reward(
    end_effector_pos: tuple[float, float, float],
    target_pos: tuple[float, float, float],
    joint_velocities: list[float],
    max_reach_distance: float = 2.0,
    velocity_penalty_weight: float = 0.01,
    success_threshold: float = 0.05,
) -> dict:
    """
    Calculate reward for a reaching task.

    Args:
        end_effector_pos: Current (x, y, z) of the robot's end effector
        target_pos: Goal (x, y, z) position
        joint_velocities: Angular velocities of each joint (for smoothness penalty)
        max_reach_distance: Maximum expected distance for normalization
        velocity_penalty_weight: How much to penalize jerky motion
        success_threshold: Distance at which task is considered complete

    Returns:
        Dict with total reward, components, and done flag
    """
    # Euclidean distance to target
    dx = end_effector_pos[0] - target_pos[0]
    dy = end_effector_pos[1] - target_pos[1]
    dz = end_effector_pos[2] - target_pos[2]
    distance = math.sqrt(dx * dx + dy * dy + dz * dz)

    # Distance reward: closer = higher (normalized 0 to 1)
    distance_reward = 1.0 - min(distance / max_reach_distance, 1.0)

    # Velocity penalty: encourage smooth motion
    velocity_magnitude = math.sqrt(sum(v * v for v in joint_velocities))
    velocity_penalty = -velocity_penalty_weight * velocity_magnitude

    # Success bonus
    success = distance < success_threshold
    success_bonus = 10.0 if success else 0.0

    total_reward = distance_reward + velocity_penalty + success_bonus

    return {
        "total_reward": total_reward,
        "distance_reward": distance_reward,
        "velocity_penalty": velocity_penalty,
        "success_bonus": success_bonus,
        "distance": distance,
        "done": success,
    }


if __name__ == "__main__":
    # Example: end effector close to target
    result = compute_reaching_reward(
        end_effector_pos=(1.0, 0.5, 0.8),
        target_pos=(1.0, 0.5, 0.85),
        joint_velocities=[0.1, 0.05, 0.02, 0.01],
    )
    print("Reward breakdown:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    # Expected output:
    #   total_reward: 10.974...
    #   distance_reward: 0.975
    #   velocity_penalty: -0.000567...
    #   success_bonus: 10.0
    #   distance: 0.05
    #   done: True
```

## Parallel Training with Environment Instances

One of ML-Agents' strengths is the ability to run multiple environment copies simultaneously, collecting experience in parallel and accelerating training dramatically. You configure this in the YAML:

```bash
# Launch training with 8 parallel environments
mlagents-learn config/robot_training.yaml \
  --run-id=humanoid_walk_v1 \
  --num-envs=8 \
  --time-scale=20

# Monitor training progress in TensorBoard
tensorboard --logdir=results --port=6006
```

With 8 parallel environments running at 20x simulation speed, you collect experience roughly 160x faster than a single real-time environment. For a humanoid walking task that needs ~2 million steps, this reduces training from days to hours.

## Exporting and Evaluating Trained Policies

After training, ML-Agents exports the policy as an ONNX model that can be loaded directly into Unity (via the Barracuda inference engine) or converted for deployment on edge devices:

The trained `.onnx` file sits in `results/<run-id>/<behavior-name>.onnx`. In Unity, you assign this model to the Agent's Behavior Parameters as the "Model" field, and the agent now runs inference instead of requesting decisions from the Python trainer.

## Key Takeaways

- Unity ML-Agents provides a complete reinforcement learning pipeline that connects Unity simulation environments to PyTorch-based training algorithms
- The observation–action–reward loop follows standard RL conventions, making ML-Agents compatible with RL research best practices
- Reward function design is the most impactful engineering decision—balance task progress, motion smoothness, and success bonuses
- Parallel environment training (multiple Unity instances) accelerates data collection by orders of magnitude
- Trained policies export as ONNX models for deployment in Unity, on edge devices, or as baselines for sim-to-real transfer
