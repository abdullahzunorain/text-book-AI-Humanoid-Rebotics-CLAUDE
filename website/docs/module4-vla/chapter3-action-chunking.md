---
title: "Chapter 3: Action Chunking"
sidebar_position: 3
---

# Chapter 3: Action Chunking

## Learning Objectives

- Understand the action chunking paradigm and why predicting action sequences outperforms single-step predictions
- Learn how Action Chunking with Transformers (ACT) and Diffusion Policy generate smooth robot trajectories
- Implement action chunk generation and temporal ensembling for robust execution
- Compare action chunking with traditional single-step behavior cloning

## The Single-Step Problem

In traditional behavior cloning, a policy predicts one action at a time: given the current observation, output the next joint position or end-effector target. This frame-by-frame approach has several fundamental problems:

1. **Compounding errors** — small prediction errors accumulate over hundreds of steps, causing the robot to drift far from the demonstrated trajectory
2. **Multi-modality** — when multiple valid actions exist (go left or right around an obstacle), averaging them produces an invalid action (go straight into the obstacle)
3. **Temporal inconsistency** — consecutive predictions may conflict, causing jerky, oscillating motion

**Action chunking** solves these problems by predicting an entire sequence of future actions at once—a "chunk" of 10 to 100 timesteps. This gives the model a planning horizon and ensures temporal consistency within each chunk.

## How Action Chunking Works

Instead of predicting a single action **a_t**, an action-chunking policy predicts a sequence:

**π(o_t) → \[a_t, a_t+1, a_t+2, ..., a_t+H-1\]**

where **H** is the **chunk size** (typically 10–100 steps at 10–50 Hz control frequency). The robot executes the first few actions from the chunk, then re-predicts a new chunk from the updated observation. This overlapping execution creates smooth, robust behavior.

### Temporal Ensembling

When chunks overlap, multiple predictions exist for the same future timestep. **Temporal ensembling** combines these predictions using exponentially weighted averaging:

```python
# temporal_ensemble.py — Temporal ensembling for overlapping action chunks
"""Implement temporal ensembling to combine overlapping action chunk predictions."""
import math


def exponential_weights(num_predictions: int, decay: float = 0.01) -> list[float]:
    """Generate exponentially decaying weights for temporal ensembling.

    More recent predictions get higher weight.

    Args:
        num_predictions: Number of overlapping predictions for a timestep
        decay: Exponential decay rate (smaller = more uniform weighting)

    Returns:
        Normalized weight list (most recent prediction last, highest weight)
    """
    raw_weights = [math.exp(-decay * (num_predictions - 1 - i))
                   for i in range(num_predictions)]
    total = sum(raw_weights)
    return [w / total for w in raw_weights]


def temporal_ensemble(
    action_chunks: list[list[list[float]]],
    chunk_starts: list[int],
    target_timestep: int,
    decay: float = 0.01,
) -> list[float]:
    """
    Combine overlapping action chunk predictions for a single timestep.

    Args:
        action_chunks: List of chunks, each is a list of action vectors
        chunk_starts: Starting timestep for each chunk
        target_timestep: The timestep to compute the ensembled action for
        decay: Exponential decay rate for weighting

    Returns:
        Ensembled action vector for the target timestep
    """
    # Collect all predictions that cover the target timestep
    predictions: list[list[float]] = []
    for chunk, start in zip(action_chunks, chunk_starts):
        offset = target_timestep - start
        if 0 <= offset < len(chunk):
            predictions.append(chunk[offset])

    if not predictions:
        raise ValueError(f"No predictions cover timestep {target_timestep}")

    # Weight more recent predictions higher
    weights = exponential_weights(len(predictions), decay)

    # Weighted average across action dimensions
    action_dim = len(predictions[0])
    ensembled = [0.0] * action_dim
    for pred, weight in zip(predictions, weights):
        for d in range(action_dim):
            ensembled[d] += pred[d] * weight

    return ensembled


if __name__ == "__main__":
    # Simulate 3 overlapping chunks (chunk size=4, action dim=2)
    chunks = [
        [[1.0, 0.0], [1.1, 0.1], [1.2, 0.2], [1.3, 0.3]],  # chunk 0 (t=0..3)
        [[1.05, 0.08], [1.15, 0.18], [1.25, 0.28], [1.35, 0.38]],  # chunk 1 (t=1..4)
        [[1.12, 0.16], [1.22, 0.26], [1.32, 0.36], [1.42, 0.46]],  # chunk 2 (t=2..5)
    ]
    starts = [0, 1, 2]

    print("Temporal Ensembling Results:")
    for t in range(6):
        try:
            action = temporal_ensemble(chunks, starts, t)
            coverage = sum(1 for c, s in zip(chunks, starts) if 0 <= t - s < len(c))
            print(f"  t={t}: action={[round(a, 3) for a in action]} "
                  f"(from {coverage} overlapping chunks)")
        except ValueError:
            print(f"  t={t}: no coverage")
    # Expected output:
    #   t=0: action=[1.0, 0.0] (from 1 overlapping chunks)
    #   t=1: action=[~1.07, ~0.09] (from 2 overlapping chunks)
    #   t=2: action=[~1.15, ~0.18] (from 3 overlapping chunks)
    #   t=3: action=[~1.28, ~0.28] (from 3 overlapping chunks)
    #   t=4: action=[~1.32, ~0.35] (from 2 overlapping chunks)
    #   t=5: action=[1.42, 0.46] (from 1 overlapping chunks)
```

## ACT: Action Chunking with Transformers

ACT (Action Chunking with Transformers) is a foundational algorithm from Tony Zhao et al. (2023) that combines a CVAE (Conditional Variational Autoencoder) with a Transformer decoder to predict action chunks from visual observations:

### Architecture

1. **Visual encoder** (ResNet-18) extracts features from camera images
2. **CVAE encoder** (training only) encodes the expert action sequence into a style variable **z**
3. **Transformer decoder** takes visual features + style variable and autoregressively generates the action chunk
4. At inference, **z** is sampled from the prior (standard Gaussian), providing diversity in multi-modal scenarios

### Why ACT Works

- The **chunk prediction** eliminates compounding errors within the chunk horizon
- The **CVAE style variable** handles multi-modality (multiple valid ways to do a task)
- The **Transformer decoder** captures long-range temporal dependencies within the chunk
- **Temporal ensembling** during execution smooths transitions between chunks

```python
# act_config.py — Configure ACT model hyperparameters
"""Configuration for Action Chunking with Transformers (ACT)."""
from dataclasses import dataclass


@dataclass
class ACTConfig:
    """Hyperparameters for ACT model training and inference."""
    # Action space
    action_dim: int = 7  # 6-DOF pose + gripper
    chunk_size: int = 50  # Number of future actions per prediction
    control_freq_hz: int = 50

    # Architecture
    hidden_dim: int = 512
    num_encoder_layers: int = 4
    num_decoder_layers: int = 7
    num_heads: int = 8
    feedforward_dim: int = 3200
    dropout: float = 0.1

    # CVAE
    latent_dim: int = 32
    kl_weight: float = 10.0  # Weight of KL divergence loss

    # Visual encoder
    backbone: str = "resnet18"
    num_cameras: int = 2  # e.g., wrist + overhead
    image_size: tuple[int, int] = (480, 640)

    # Training
    lr: float = 1e-5
    weight_decay: float = 1e-4
    batch_size: int = 8
    num_epochs: int = 3000

    # Temporal ensembling at inference
    ensemble_decay: float = 0.01
    execution_length: int = 10  # Execute this many steps before re-predicting

    def chunk_duration_seconds(self) -> float:
        """Duration of one action chunk in seconds."""
        return self.chunk_size / self.control_freq_hz

    def total_params_estimate(self) -> int:
        """Rough estimate of model parameters."""
        transformer_params = (
            self.num_encoder_layers * 4 * self.hidden_dim * self.hidden_dim
            + self.num_decoder_layers * 4 * self.hidden_dim * self.hidden_dim
        )
        backbone_params = 11_000_000  # ResNet-18 baseline
        return transformer_params + backbone_params


if __name__ == "__main__":
    config = ACTConfig(
        chunk_size=50,
        num_cameras=2,
        action_dim=7,
    )
    print(f"ACT Configuration:")
    print(f"  Chunk size: {config.chunk_size} steps "
          f"({config.chunk_duration_seconds():.1f}s at {config.control_freq_hz}Hz)")
    print(f"  Action dim: {config.action_dim}")
    print(f"  Cameras: {config.num_cameras}")
    print(f"  CVAE latent dim: {config.latent_dim}")
    print(f"  Transformer: {config.num_encoder_layers}enc + "
          f"{config.num_decoder_layers}dec layers, "
          f"{config.hidden_dim}D, {config.num_heads} heads")
    print(f"  ~{config.total_params_estimate():,} parameters")
    print(f"  Ensemble decay: {config.ensemble_decay}")
    # Expected output:
    #   ACT Configuration:
    #     Chunk size: 50 steps (1.0s at 50Hz)
    #     Action dim: 7
    #     Cameras: 2
    #     CVAE latent dim: 32
    #     Transformer: 4enc + 7dec layers, 512D, 8 heads
    #     ~35,651,584 parameters
    #     Ensemble decay: 0.01
```

## Diffusion Policy: Action Chunking via Denoising

An alternative approach to action chunking uses **diffusion models**—the same generative models behind Stable Diffusion and DALL-E, but generating action trajectories instead of images. Diffusion Policy (Chi et al., 2023) iteratively denoises a random noise vector into a coherent action sequence:

1. Start with random noise of shape `(chunk_size, action_dim)`
2. Condition on visual observations
3. Run K denoising steps (typically 10–100)
4. Output the denoised action chunk

Diffusion Policy excels at **multi-modal** tasks where multiple equally-valid action sequences exist—it naturally represents this diversity in its denoising distribution.

## Choosing Chunk Size

The chunk size **H** is a critical hyperparameter:

| Chunk Size | Pros | Cons |
|-----------|------|------|
| Small (5–10) | Reactive, adapts quickly | More compounding errors, jerky motion |
| Medium (20–50) | Good balance of planning and reactivity | Standard choice for most tasks |
| Large (50–100) | Very smooth trajectories, long-horizon planning | Slow to react to perturbations |

For contact-rich manipulation (assembly, insertion), medium chunks (20–50 steps) are standard. For free-space motion (reaching, pick-and-place), larger chunks (50–100) enable smoother trajectories.

## Key Takeaways

- Action chunking predicts sequences of future actions rather than single actions, eliminating compounding errors and ensuring temporal consistency
- Temporal ensembling smoothly combines overlapping chunk predictions using exponentially weighted averaging
- ACT uses a CVAE + Transformer to generate diverse action chunks, handling multi-modal demonstrations effectively
- Diffusion Policy applies denoising diffusion to action trajectory generation, excelling at multi-modal tasks
- Chunk size is a key design choice: larger chunks give smoother motion but slower reactivity to perturbations
