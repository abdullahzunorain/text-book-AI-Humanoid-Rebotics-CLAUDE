"""
Translation service: extract code blocks from markdown, translate prose to Urdu via LLMClient,
and re-insert original code blocks unchanged. Results are cached per user+chapter.

Public API:
    extract_code_blocks(markdown) -> (prose_with_placeholders, code_blocks)
    translate_to_urdu(chapter_markdown, user_id, chapter_slug) -> {"translated_content": str, "original_code_blocks": list[str]}
"""

from __future__ import annotations

import re

from services.cache_service import get_cached, set_cached
from services.agent_config import run_agent, translation_agent

# ---------------------------------------------------------------------------
# Code-block extraction
# ---------------------------------------------------------------------------

_CODE_BLOCK_RE: re.Pattern[str] = re.compile(
    r"(```[\s\S]*?```)", re.MULTILINE
)


def extract_code_blocks(markdown: str) -> tuple[str, list[str]]:
    """Replace fenced code blocks with numbered placeholders.

    Args:
        markdown: Raw chapter markdown.

    Returns:
        A tuple of (prose_with_placeholders, list_of_original_code_blocks).
    """
    blocks: list[str] = _CODE_BLOCK_RE.findall(markdown)
    prose: str = markdown
    for idx, block in enumerate(blocks):
        prose = prose.replace(block, f"{{{{CODE_BLOCK_{idx}}}}}", 1)
    return prose, blocks


# ---------------------------------------------------------------------------
# Translation prompt
# ---------------------------------------------------------------------------

_TRANSLATE_SYSTEM = (
    "You are a professional Urdu translator for educational robotics content."
)

_TRANSLATE_PROMPT_TEMPLATE = (
    "Translate the following Markdown text from English to Urdu.\n\n"
    "RULES:\n"
    "1. Translate ALL prose to natural, formal Urdu (Nastaliq script).\n"
    "2. Keep ALL technical terms in English (ROS 2, Gazebo, Python, URDF, etc.).\n"
    "3. Keep ALL markdown formatting (headers #, bold **, lists -, tables, links).\n"
    "4. Keep ALL {{CODE_BLOCK_N}} placeholders EXACTLY as they are — do NOT translate them.\n"
    "5. Preserve paragraph structure.\n\n"
    "TEXT TO TRANSLATE:\n\n"
    "{prose}"
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def translate_to_urdu(
    chapter_markdown: str,
    *,
    user_id: int,
    chapter_slug: str,
) -> dict[str, str | list[str]]:
    """Translate a chapter markdown to Urdu, preserving code blocks.

    Checks cache first; on miss, calls LLMClient with failover and caches the result.

    Args:
        chapter_markdown: Full chapter markdown content.
        user_id: Authenticated user id (for cache key).
        chapter_slug: Chapter slug (for cache key).

    Returns:
        Dict with ``translated_content`` (full Urdu markdown with code blocks)
        and ``original_code_blocks`` (list of original fenced blocks).
    """
    prose, blocks = extract_code_blocks(chapter_markdown)

    # Check cache first
    cached = await get_cached(user_id, chapter_slug, "translation")
    if cached is not None:
        return {
            "translated_content": cached,
            "original_code_blocks": blocks,
        }

    # Call Translation Agent
    prompt = _TRANSLATE_PROMPT_TEMPLATE.format(prose=prose)
    translated_prose: str = await run_agent(translation_agent, input=prompt)

    # Re-insert original code blocks at placeholder positions
    for idx, block in enumerate(blocks):
        translated_prose = translated_prose.replace(
            f"{{{{CODE_BLOCK_{idx}}}}}", block
        )

    # Cache the result (translation cache is never invalidated by profile update)
    await set_cached(
        user_id=user_id,
        chapter_slug=chapter_slug,
        cache_type="translation",
        content=translated_prose,
        metadata={},
    )

    return {
        "translated_content": translated_prose,
        "original_code_blocks": blocks,
    }
