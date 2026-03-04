---
title: "Chapter 4: Isaac Reinforcement Learning"
sidebar_position: 4
---

# Chapter 4: Isaac Reinforcement Learning

## Learning Objectives

- Understand the Omniverse Isaac Gym Reinforcement Learning (OmniIsaacGymEnvs) framework and how it extends Isaac Gym
- Design task environments for manipulation and locomotion with full Isaac Sim fidelity
- Implement curriculum learning and asymmetric actor-critic for complex robotics tasks
- Deploy trained policies from Isaac Sim to real robots via the sim-to-real transfer pipeline

## From Isaac Gym to OmniIsaacGymEnvs

While Isaac Gym (Chapter 2) provides blazing-fast GPU-parallel physics for RL training, it uses simplified visual rendering. **OmniIsaacGymEnvs (OIGE)** combines Isaac Gym's GPU-parallel training speed with Isaac Sim's full-fidelity rendering and sensor simulation. This gives you the best of both worlds: train at thousands-of-environments scale while periodically rendering photorealistic images for vision-based policy evaluation.

OIGE is built on top of the `omni.isaac.gym` extension and follows the same environment interface as Isaac Gym, so if you've already built Isaac Gym environments, migrating to OIGE is straightforward. The key addition is access to USD assets, RTX rendering, and the full Omniverse ecosystem.

### When to Use OIGE vs Isaac Gym

| Scenario | Recommended |
|----------|-------------|
| State-based RL (joint positions, velocities) | Isaac Gym — faster, simpler |
| Vision-based RL (camera images as observations) | OIGE — RTX rendering needed |
| Large-scale parallel training (>4096 envs) | Isaac Gym — lower overhead |
| Sim-to-real with visual domain randomization | OIGE — built-in randomizers |
| Manipulation with SDF collision checking | OIGE — PhysX 5 SDF support |

## Designing an RL Task in OIGE

Each OIGE task is a Python class that inherits from `RLTask` and defines the observation computation, action application, reward function, and reset logic. Here's a configuration and trait system for building tasks:

```python
# rl_task_builder.py — Build an OIGE RL task configuration
"""Define and validate an OmniIsaacGymEnvs RL task configuration."""
from dataclasses import dataclass, field
from enum import Enum


class TaskType(Enum):
    """Supported RL task categories."""
    LOCOMOTION = "locomotion"
    MANIPULATION = "manipulation"
    NAVIGATION = "navigation"
    WHOLE_BODY = "whole_body"


@dataclass
class ObservationSpec:
    """Defines the observation space for an RL task."""
    joint_positions: bool = True
    joint_velocities: bool = True
    base_orientation: bool = True
    base_angular_velocity: bool = True
    base_linear_velocity: bool = True
    gravity_projection: bool = True
    previous_actions: bool = True
    target_position: bool = False
    camera_image: bool = False
    camera_resolution: tuple[int, int] = (84, 84)

    def compute_dim(self, num_dofs: int) -> int:
        """Compute total observation dimension."""
        dim = 0
        if self.joint_positions:
            dim += num_dofs
        if self.joint_velocities:
            dim += num_dofs
        if self.base_orientation:
            dim += 4  # quaternion
        if self.base_angular_velocity:
            dim += 3
        if self.base_linear_velocity:
            dim += 3
        if self.gravity_projection:
            dim += 3
        if self.previous_actions:
            dim += num_dofs
        if self.target_position:
            dim += 3
        return dim


@dataclass
class RewardComponent:
    """A single component of a composite reward function."""
    name: str
    weight: float
    description: str
    requires_termination: bool = False


@dataclass
class RLTaskConfig:
    """Full configuration for an OmniIsaacGymEnvs RL task."""
    task_name: str
    task_type: TaskType
    robot_asset: str
    num_envs: int = 2048
    num_dofs: int = 7
    episode_length: int = 500
    control_frequency: int = 20  # Hz
    observation_spec: ObservationSpec = field(default_factory=ObservationSpec)
    reward_components: list[RewardComponent] = field(default_factory=list)

    # Curriculum settings
    use_curriculum: bool = False
    curriculum_stages: int = 5
    difficulty_metric: str = "success_rate"
    advancement_threshold: float = 0.8

    # Domain randomization
    randomize_friction: bool = True
    randomize_mass: bool = True
    randomize_gravity: bool = False
    add_observation_noise: bool = True
    noise_scale: float = 0.01


def build_franka_reach_task() -> RLTaskConfig:
    """Build a Franka reach task — robot arm must touch a target cube."""
    obs_spec = ObservationSpec(
        target_position=True,
        camera_image=False,
    )

    rewards = [
        RewardComponent("distance", -1.0, "Negative distance to target"),
        RewardComponent("success", 10.0, "Bonus when within 2cm of target"),
        RewardComponent("action_penalty", -0.01, "Penalize large actions"),
        RewardComponent("velocity_penalty", -0.001, "Penalize fast joint motion"),
    ]

    return RLTaskConfig(
        task_name="FrankaReach",
        task_type=TaskType.MANIPULATION,
        robot_asset="/Isaac/Robots/Franka/franka_alt_fingers.usd",
        num_envs=2048,
        num_dofs=9,  # 7 arm + 2 gripper
        episode_length=200,
        control_frequency=20,
        observation_spec=obs_spec,
        reward_components=rewards,
        use_curriculum=False,
    )


def summarize_task(config: RLTaskConfig) -> dict:
    """Generate a summary of the task configuration."""
    obs_dim = config.observation_spec.compute_dim(config.num_dofs)
    total_reward_weight = sum(abs(r.weight) for r in config.reward_components)

    return {
        "task_name": config.task_name,
        "task_type": config.task_type.value,
        "num_envs": config.num_envs,
        "obs_dim": obs_dim,
        "action_dim": config.num_dofs,
        "reward_components": len(config.reward_components),
        "total_reward_weight": total_reward_weight,
        "curriculum": config.use_curriculum,
        "domain_randomization": any([
            config.randomize_friction,
            config.randomize_mass,
            config.randomize_gravity,
        ]),
    }


if __name__ == "__main__":
    task = build_franka_reach_task()
    summary = summarize_task(task)
    print(f"Task: {summary['task_name']} ({summary['task_type']})")
    print(f"Environments: {summary['num_envs']}")
    print(f"Observation dim: {summary['obs_dim']}, Action dim: {summary['action_dim']}")
    print(f"Reward components: {summary['reward_components']}")
    print(f"Curriculum: {summary['curriculum']}")
    print(f"Domain randomization: {summary['domain_randomization']}")
    print("\nReward breakdown:")
    for r in task.reward_components:
        print(f"  {r.name}: weight={r.weight}, {r.description}")
    # Expected output:
    #   Task: FrankaReach (manipulation)
    #   Environments: 2048
    #   Observation dim: 39, Action dim: 9
    #   Reward components: 4
    #   Curriculum: False
    #   Domain randomization: True
```

## Curriculum Learning for Complex Tasks

Some tasks—like humanoid walking on rough terrain—are too hard for RL to solve from scratch. Curriculum learning incrementally increases task difficulty as the agent improves:

1. **Stage 1**: Walk on flat ground (easy)
2. **Stage 2**: Walk on slightly uneven terrain
3. **Stage 3**: Walk on random hills with small obstacles
4. **Stage 4**: Walk on steep slopes with pushes
5. **Stage 5**: Walk on rough terrain with varying friction and payloads

The advancement criterion is typically a success rate threshold: once the agent succeeds >80% of episodes at the current difficulty, the environment advances to the next stage.

## Asymmetric Actor-Critic

A powerful technique in sim-to-real RL is **asymmetric actor-critic**, where the critic network receives privileged information (ground truth contact forces, exact object poses) while the actor only sees realistic observations (noisy joint encoders, estimated poses). This gives the critic a richer signal for value estimation during training, while the actor learns a policy that relies only on information available on the real robot.

```python
# asymmetric_config.py — Asymmetric actor-critic observation split
"""Define observation splits for asymmetric actor-critic training."""


def build_asymmetric_observations(
    num_dofs: int = 21,
    include_privileged: bool = True,
) -> dict:
    """
    Build observation specifications for asymmetric actor-critic.

    Actor (policy) receives only realistic observations.
    Critic receives actor observations + privileged ground truth.
    """
    # Actor observations — available on real robot
    actor_obs = {
        "joint_positions": num_dofs,
        "joint_velocities": num_dofs,
        "base_orientation_quat": 4,
        "base_angular_velocity": 3,
        "base_linear_velocity": 3,
        "gravity_in_body_frame": 3,
        "previous_actions": num_dofs,
        "noisy_height_scan": 100,  # terrain heightmap with noise
    }

    actor_dim = sum(actor_obs.values())

    if not include_privileged:
        return {
            "actor_obs": actor_obs,
            "actor_dim": actor_dim,
            "critic_obs": actor_obs,
            "critic_dim": actor_dim,
            "privileged_dim": 0,
        }

    # Privileged observations — only available in simulation
    privileged_obs = {
        "ground_truth_contact_forces": 4 * 3,   # 4 feet × 3D force
        "true_terrain_height": 100,              # exact heightmap (no noise)
        "external_force_applied": 3,             # random push force
        "true_friction_coefficient": 1,          # actual ground friction
        "true_mass": 1,                          # actual robot mass
    }

    privileged_dim = sum(privileged_obs.values())
    critic_dim = actor_dim + privileged_dim

    return {
        "actor_obs": actor_obs,
        "actor_dim": actor_dim,
        "privileged_obs": privileged_obs,
        "privileged_dim": privileged_dim,
        "critic_dim": critic_dim,
    }


if __name__ == "__main__":
    result = build_asymmetric_observations(num_dofs=21)
    print("Asymmetric Actor-Critic Observation Split:")
    print(f"\nActor observation dim: {result['actor_dim']}")
    for name, dim in result['actor_obs'].items():
        print(f"  {name}: {dim}")
    print(f"\nPrivileged observation dim: {result['privileged_dim']}")
    for name, dim in result['privileged_obs'].items():
        print(f"  {name}: {dim}")
    print(f"\nCritic total dim: {result['critic_dim']}")
    # Expected output:
    #   Actor observation dim: 176
    #   Critic total dim: 293
```

## Sim-to-Real Transfer Pipeline

The final step in the Isaac RL workflow is deploying trained policies to real hardware. The pipeline follows these stages:

1. **Train in simulation** with domain randomization and asymmetric actor-critic
2. **Evaluate in simulation** with rendering enabled to visually inspect behavior
3. **Export the actor network** as an ONNX model (critic is discarded)
4. **Integrate with robot SDK** — load the ONNX model with ONNX Runtime or TensorRT
5. **Deploy incrementally** — start with low gains and conservative action limits
6. **Fine-tune on device** — optional online adaptation using real sensor data

The key to successful transfer is training with enough domain randomization that the policy has "seen" the real world's variability during simulation. This is why Isaac Sim's high-fidelity physics and rendering—combined with Isaac Gym's massive parallel scale—form such a powerful combination for real-world robot deployment.

## Key Takeaways

- OmniIsaacGymEnvs combines Isaac Gym's GPU-parallel training speed with Isaac Sim's photorealistic rendering for vision-based RL
- Curriculum learning gradually increases task difficulty to solve problems too hard for flat RL exploration
- Asymmetric actor-critic uses privileged simulation data for the critic while keeping the actor's observations realistic, improving sim-to-real transfer
- The sim-to-real pipeline flows from GPU-parallel training → domain randomization → ONNX export → robot deployment
- Task design requires careful specification of observations, actions, rewards, and termination conditions—each choice directly impacts training stability and final policy quality
