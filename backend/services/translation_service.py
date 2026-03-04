"""
Translation service: extract code blocks from markdown, translate prose to Urdu via Gemini,
and re-insert original code blocks unchanged.

Public API:
    extract_code_blocks(markdown) -> (prose_with_placeholders, code_blocks)
    translate_to_urdu(chapter_markdown) -> {"translated_content": str, "original_code_blocks": list[str]}
"""

from __future__ import annotations

import os
import re

from google import genai

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
# Gemini translation helper (internal)
# ---------------------------------------------------------------------------


async def _call_gemini_translate(prose: str) -> str:
    """Call Gemini gemini-2.5-flash to translate prose to Urdu.

    The prose already has code blocks replaced with {{CODE_BLOCK_N}} placeholders.
    The prompt instructs Gemini to keep placeholders as-is.
    """
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY", ""))

    prompt: str = (
        "You are a professional Urdu translator for educational robotics content.\n"
        "Translate the following Markdown text from English to Urdu.\n\n"
        "RULES:\n"
        "1. Translate ALL prose to natural, formal Urdu (Nastaliq script).\n"
        "2. Keep ALL technical terms in English (ROS 2, Gazebo, Python, URDF, etc.).\n"
        "3. Keep ALL markdown formatting (headers #, bold **, lists -, tables, links).\n"
        "4. Keep ALL {{CODE_BLOCK_N}} placeholders EXACTLY as they are — do NOT translate them.\n"
        "5. Preserve paragraph structure.\n\n"
        "TEXT TO TRANSLATE:\n\n"
        f"{prose}"
    )

    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text or ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def translate_to_urdu(chapter_markdown: str) -> dict[str, str | list[str]]:
    """Translate a chapter markdown to Urdu, preserving code blocks.

    Args:
        chapter_markdown: Full chapter markdown content.

    Returns:
        Dict with ``translated_content`` (full Urdu markdown with code blocks)
        and ``original_code_blocks`` (list of original fenced blocks).
    """
    prose, blocks = extract_code_blocks(chapter_markdown)

    translated_prose: str = await _call_gemini_translate(prose)

    # Re-insert original code blocks at placeholder positions
    for idx, block in enumerate(blocks):
        translated_prose = translated_prose.replace(
            f"{{{{CODE_BLOCK_{idx}}}}}", block
        )

    return {
        "translated_content": translated_prose,
        "original_code_blocks": blocks,
    }
