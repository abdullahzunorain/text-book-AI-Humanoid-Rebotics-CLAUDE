---
title: "Chapter 2: Multimodal Models"
sidebar_position: 2
---

# Chapter 2: Multimodal Models for Robotics

## Learning Objectives

- Understand how multimodal foundation models process and align vision and language representations
- Learn the key architectures (CLIP, Flamingo, GPT-4V) that underpin VLA models
- Implement embedding space analysis to visualize how vision and language representations align
- Evaluate the tradeoffs between frozen backbones and end-to-end fine-tuning for robotics applications

## What Are Multimodal Models?

Multimodal models are neural networks that process and reason over multiple types of data—typically images and text—within a unified architecture. In the context of robotics, these models provide the **perceptual intelligence** that allows a robot to understand both what it sees and what it's told to do.

The core insight is that images and text can be mapped into a **shared embedding space** where semantically similar concepts (like the image of a cup and the word "cup") are close together. This alignment enables zero-shot transfer: a model that has never seen a specific object during training can still understand instructions about it at deployment time, because the language description and visual appearance map to the same region of embedding space.

### The Alignment Problem

Traditional computer vision models output class labels from a fixed set ("cat", "dog", "car"). This is useless for robotics, where the set of objects, states, and tasks is effectively infinite. Multimodal models solve this by learning **open-vocabulary** representations—they understand arbitrary concepts described in natural language, even if those concepts were never seen during training.

## CLIP: The Foundation of Visual-Language Alignment

CLIP (Contrastive Language-Image Pre-training) from OpenAI is the most influential multimodal model for robotics. It learns to align images and text by training on 400 million image-text pairs collected from the internet.

### How CLIP Works

1. An **image encoder** (ViT or ResNet) maps an image to a vector
2. A **text encoder** (Transformer) maps a text description to a vector
3. Training maximizes the cosine similarity between matching pairs and minimizes it for non-matching pairs

This contrastive objective creates an embedding space where:
- "A photo of a red mug" and an image of a red mug → high similarity
- "A photo of a red mug" and an image of a blue plate → low similarity

```python
# clip_similarity.py — Analyze CLIP-style similarity scores
"""Demonstrate vision-language similarity scoring for robotics objects."""
import math
from dataclasses import dataclass


@dataclass
class Embedding:
    """Simulated embedding vector with a label."""
    label: str
    modality: str  # "image" or "text"
    vector: list[float]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def build_robotics_embeddings() -> list[Embedding]:
    """Create simulated embeddings for common robotics objects.

    In practice, these would come from a real CLIP model.
    Here we use hand-crafted vectors to demonstrate the concept.
    """
    embeddings = [
        # Image embeddings (simulated)
        Embedding("red_mug_image", "image",    [0.9, 0.1, 0.2, 0.0, 0.3]),
        Embedding("blue_plate_image", "image",  [0.1, 0.8, 0.1, 0.2, 0.1]),
        Embedding("robot_arm_image", "image",   [0.2, 0.1, 0.9, 0.7, 0.5]),
        # Text embeddings (simulated)
        Embedding("red mug", "text",            [0.85, 0.15, 0.25, 0.05, 0.28]),
        Embedding("blue plate", "text",         [0.15, 0.75, 0.12, 0.18, 0.08]),
        Embedding("pick up the mug", "text",    [0.7, 0.1, 0.5, 0.3, 0.4]),
        Embedding("robotic manipulator", "text", [0.25, 0.12, 0.85, 0.65, 0.48]),
    ]
    return embeddings


def compute_similarity_matrix(embeddings: list[Embedding]) -> list[list[float]]:
    """Compute pairwise cosine similarity between all embeddings."""
    n = len(embeddings)
    matrix: list[list[float]] = []
    for i in range(n):
        row: list[float] = []
        for j in range(n):
            sim = cosine_similarity(embeddings[i].vector, embeddings[j].vector)
            row.append(round(sim, 3))
        matrix.append(row)
    return matrix


if __name__ == "__main__":
    embeddings = build_robotics_embeddings()
    matrix = compute_similarity_matrix(embeddings)

    # Print header
    labels = [e.label for e in embeddings]
    max_label = max(len(l) for l in labels)
    header = " " * (max_label + 2) + "  ".join(f"{i}" for i in range(len(labels)))
    print("Cosine Similarity Matrix:")
    print(f"{'Label':<{max_label+2}} " + " ".join(f"{i:>5}" for i in range(len(labels))))

    for i, row in enumerate(matrix):
        values = " ".join(f"{v:>5.2f}" for v in row)
        print(f"{labels[i]:<{max_label+2}} {values}")

    # Show highest cross-modal similarities
    print("\nTop cross-modal matches:")
    images = [(i, e) for i, e in enumerate(embeddings) if e.modality == "image"]
    texts = [(i, e) for i, e in enumerate(embeddings) if e.modality == "text"]

    for img_idx, img in images:
        best_text = max(texts, key=lambda t: matrix[img_idx][t[0]])
        print(f"  {img.label} → {best_text[1].label} (sim={matrix[img_idx][best_text[0]]:.3f})")
```

## From CLIP to Robotics: Grounding Language in Action

CLIP aligns vision and language, but it doesn't produce actions. The bridge from multimodal understanding to robot control requires one of these strategies:

### Strategy 1: Score and Select

Use CLIP to score candidate actions. Given a language instruction and the current image, generate several possible next states (via a forward model or imagination) and select the one whose image embedding best matches the instruction embedding.

### Strategy 2: Embed and Decode

Concatenate the CLIP image and text embeddings and feed them to a learned action decoder network. This is the approach used by RT-2 and OpenVLA.

### Strategy 3: Fine-tune End-to-End

Replace CLIP's contrastive loss with a behavior cloning loss: given (image, instruction) pairs from demonstrations, predict the expert's action. The vision and language encoders are fine-tuned jointly.

```python
# grounding_strategy.py — Compare VLA grounding strategies
"""Compare strategies for grounding language in robot actions."""
from dataclasses import dataclass


@dataclass
class GroundingStrategy:
    """A strategy for converting vision+language into robot actions."""
    name: str
    approach: str
    pros: list[str]
    cons: list[str]
    example_models: list[str]
    typical_latency_ms: int


def compare_strategies() -> list[GroundingStrategy]:
    """Define and compare the main grounding strategies."""
    return [
        GroundingStrategy(
            name="Score and Select",
            approach="Use VLM as a scorer over candidate actions",
            pros=[
                "No action-space fine-tuning needed",
                "Modular — can swap VLM backbone",
                "Interpretable scoring",
            ],
            cons=[
                "Requires explicit action candidates",
                "Combinatorial explosion for continuous actions",
                "Multiple VLM forward passes per step",
            ],
            example_models=["SayCan", "InnerMonologue"],
            typical_latency_ms=500,
        ),
        GroundingStrategy(
            name="Embed and Decode",
            approach="Concatenate VL embeddings, decode to actions",
            pros=[
                "Single forward pass for action",
                "Continuous action output",
                "Leverages pretrained VL features",
            ],
            cons=[
                "Requires demonstration data for decoder training",
                "Embedding bottleneck may lose spatial detail",
            ],
            example_models=["RT-2", "OpenVLA"],
            typical_latency_ms=100,
        ),
        GroundingStrategy(
            name="End-to-End Fine-tune",
            approach="Fine-tune entire VLM with action prediction head",
            pros=[
                "Highest potential accuracy",
                "Adapts visual features for robotics",
                "Single unified model",
            ],
            cons=[
                "Expensive fine-tuning (GPU hours/days)",
                "Risk of catastrophic forgetting",
                "Large model → slower inference",
            ],
            example_models=["Octo", "π₀"],
            typical_latency_ms=150,
        ),
    ]


if __name__ == "__main__":
    strategies = compare_strategies()
    for s in strategies:
        print(f"\n{'='*50}")
        print(f"Strategy: {s.name}")
        print(f"Approach: {s.approach}")
        print(f"Latency: ~{s.typical_latency_ms}ms")
        print(f"Models: {', '.join(s.example_models)}")
        print(f"Pros: {', '.join(s.pros)}")
        print(f"Cons: {', '.join(s.cons)}")
    # Expected output: Three strategy blocks with comparison details
```

## Frozen vs Fine-tuned Backbones

A critical engineering decision when building VLA models is whether to **freeze** the pretrained vision-language backbone or **fine-tune** it on robot data:

- **Frozen backbone**: faster training, preserves general knowledge, but may lack task-specific features. Best when robot data is limited.
- **Fine-tuned backbone**: better task performance, but requires more data and risks forgetting pre-trained knowledge.

Most successful VLA models use a **partial fine-tuning** approach: freeze the language encoder (which already understands instructions) and fine-tune the vision encoder (to learn task-relevant visual features like object grasp points).

## Key Takeaways

- Multimodal models align vision and language in a shared embedding space, enabling open-vocabulary understanding of objects, scenes, and instructions
- CLIP's contrastive learning creates embeddings where semantically similar images and text are close together—the foundation for VLA perception
- Three strategies bridge multimodal understanding to robot actions: score-and-select, embed-and-decode, and end-to-end fine-tuning
- The choice between frozen and fine-tuned backbones depends on available robot demonstration data and the desired tradeoff between generalization and task performance
- Multimodal representations are the perceptual core of VLA models—without strong vision-language alignment, a robot cannot understand what you ask it to do
