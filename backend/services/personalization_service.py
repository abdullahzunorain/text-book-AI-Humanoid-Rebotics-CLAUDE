"""
Personalization service: adapt chapter content to user's educational background via LLMClient.

Public API:
    build_personalization_prompt(chapter_md, profile) -> str
    personalize_chapter(chapter_slug, user_id) -> {"personalized_content": str}
"""

from __future__ import annotations

import os
import pathlib

from db import get_pool
from services.cache_service import get_cached, set_cached
from services.agent_config import run_agent, personalization_agent
from services.translation_service import extract_code_blocks

# ---------------------------------------------------------------------------
# Default profile values (FR-037)
# ---------------------------------------------------------------------------

_DEFAULTS: dict[str, str | bool] = {
    "python_level": "beginner",
    "robotics_experience": "none",
    "math_level": "high_school",
    "hardware_access": False,
    "learning_goal": "",
}


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


def build_personalization_prompt(chapter_md: str, profile: dict[str, str | bool]) -> str:
    """Build a Gemini prompt that personalises chapter prose for the learner.

    Missing profile fields are filled with FR-037 beginner defaults.
    Code blocks are extracted and replaced with placeholders so the LLM
    is explicitly instructed to keep them unchanged (FR-033).

    Args:
        chapter_md: Raw chapter markdown.
        profile: User background dict (may be partial or empty).

    Returns:
        Full prompt string ready for Gemini.
    """
    # Merge with defaults
    merged: dict[str, str | bool] = {**_DEFAULTS, **profile}

    # Extract code blocks so the LLM only sees prose + placeholders
    prose_with_placeholders, _blocks = extract_code_blocks(chapter_md)

    prompt: str = (
        "You are an AI tutor for the \"AI and Humanoid Robotics\" textbook.\n\n"
        "Student Profile:\n"
        f"- Python Level: {merged['python_level']}\n"
        f"- Robotics Experience: {merged['robotics_experience']}\n"
        f"- Math Level: {merged['math_level']}\n"
        f"- Hardware Access: {merged['hardware_access']}\n"
        f"- Learning Goal: {merged['learning_goal']}\n\n"
        "Adaptation Rules:\n"
        "- If python_level is \"beginner\": add inline code comments, explain imports\n"
        "- If python_level is \"advanced\": focus on architecture patterns, skip basic syntax\n"
        "- If robotics_experience is \"none\": add analogies to everyday objects, explain jargon\n"
        "- If hardware_access is false: replace hardware exercises with simulator alternatives\n"
        "- If math_level is \"high_school\": avoid matrix notation, use intuitive explanations\n"
        "- If learning_goal mentions \"job\" or \"career\": add industry context\n\n"
        "IMPORTANT — Code block preservation (FR-033):\n"
        "- Keep ALL {{CODE_BLOCK_N}} placeholders EXACTLY as-is — do NOT modify, translate, "
        "or remove them. Code blocks must remain unchanged.\n"
        "- Only adapt the surrounding prose.\n\n"
        "Chapter content to personalise:\n\n"
        f"{prose_with_placeholders}"
    )
    return prompt


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_DOCS_ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent.parent / "website" / "docs"


async def personalize_chapter(chapter_slug: str, user_id: int) -> dict[str, str]:
    """Personalise a chapter for a specific user.

    1. Read chapter markdown from ``website/docs/{slug}.md``.
    2. Fetch user background from DB (or use defaults).
    3. Build prompt, call Gemini, re-insert code blocks.

    Args:
        chapter_slug: Slash-separated chapter path (e.g. ``module-1/forward-kinematics``).
        user_id: Authenticated user id.

    Returns:
        Dict with ``personalized_content`` (full personalised markdown with code blocks).
    """
    # 1. Read chapter file — 3-step resolution to handle Docusaurus numeric-prefix stripping:
    #   a. Exact:  docs/{slug}.md
    #   b. Index:  docs/{slug}/index.md
    #   c. Prefix: docs/parent/*-{basename}.md  (e.g. 01-architecture.md for slug 'architecture')
    _candidates_to_try = [
        _DOCS_ROOT / f"{chapter_slug}.md",
        _DOCS_ROOT / chapter_slug / "index.md",
    ]
    chapter_md: str | None = None
    for _candidate in _candidates_to_try:
        try:
            with open(_candidate, encoding="utf-8") as fh:
                chapter_md = fh.read()
            break
        except FileNotFoundError:
            continue
    if chapter_md is None:
        # Docusaurus strips numeric prefixes ("01-") from URLs but files keep them
        _parent = _DOCS_ROOT / pathlib.Path(chapter_slug).parent
        _basename = pathlib.Path(chapter_slug).name
        _prefix_matches = sorted(_parent.glob(f"*-{_basename}.md"))
        if not _prefix_matches:
            raise FileNotFoundError(f"Chapter not found: {chapter_slug}")
        with open(_prefix_matches[0], encoding="utf-8") as fh:
            chapter_md = fh.read()

    # 2. Fetch user background
    pool = get_pool()
    row = await pool.fetchrow(
        "SELECT python_level, robotics_experience, math_level, hardware_access, learning_goal "
        "FROM user_backgrounds WHERE user_id = $1",
        user_id,
    )
    profile: dict[str, str | bool] = dict(row) if row else {}

    # 3. Check cache first (FR-034)
    cached = await get_cached(user_id, chapter_slug, "personalization")
    if cached is not None:
        return {"personalized_content": cached}

    # 4. Extract code blocks, build prompt, call Agent
    _prose, blocks = extract_code_blocks(chapter_md)
    prompt: str = build_personalization_prompt(chapter_md, profile)

    personalised_text: str = await run_agent(personalization_agent, input=prompt)

    # 5. Re-insert original code blocks at placeholder positions
    for idx, block in enumerate(blocks):
        personalised_text = personalised_text.replace(
            f"{{{{CODE_BLOCK_{idx}}}}}", block
        )

    # 6. Cache the result (FR-033)
    await set_cached(
        user_id=user_id,
        chapter_slug=chapter_slug,
        cache_type="personalization",
        content=personalised_text,
        metadata={"profile": {k: str(v) for k, v in profile.items()}},
    )

    return {"personalized_content": personalised_text}
