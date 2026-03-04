"""
Unit tests for translation service — code-block extraction and Urdu translation.

TDD: These tests are written first and MUST FAIL until the service is implemented (C2).

Tests cover:
- extract_code_blocks() returns correct placeholder prose + block list
- translate_to_urdu() returns translated_content string and original_code_blocks list
- Code block re-insertion after translation preserves original blocks
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestExtractCodeBlocks:
    """Tests for extract_code_blocks() helper."""

    def test_extracts_single_code_block(self) -> None:
        """Single fenced code block is replaced with placeholder."""
        from services.translation_service import extract_code_blocks

        markdown: str = (
            "Some text\n\n```python\nimport rclpy\n```\n\nMore text"
        )
        prose, blocks = extract_code_blocks(markdown)

        assert len(blocks) == 1
        assert blocks[0] == "```python\nimport rclpy\n```"
        assert "{{CODE_BLOCK_0}}" in prose
        assert "```python" not in prose

    def test_extracts_multiple_code_blocks(self) -> None:
        """Multiple fenced code blocks each get unique placeholders."""
        from services.translation_service import extract_code_blocks

        markdown: str = (
            "Intro\n\n```python\nprint('hello')\n```\n\n"
            "Middle\n\n```bash\nros2 run pkg node\n```\n\nEnd"
        )
        prose, blocks = extract_code_blocks(markdown)

        assert len(blocks) == 2
        assert "{{CODE_BLOCK_0}}" in prose
        assert "{{CODE_BLOCK_1}}" in prose
        assert "```python" not in prose
        assert "```bash" not in prose

    def test_no_code_blocks_returns_original(self) -> None:
        """Markdown without code blocks returns unchanged prose and empty list."""
        from services.translation_service import extract_code_blocks

        markdown: str = "Just plain text\n\nWith paragraphs"
        prose, blocks = extract_code_blocks(markdown)

        assert prose == markdown
        assert blocks == []

    def test_preserves_text_around_blocks(self) -> None:
        """Text before and after code blocks is preserved."""
        from services.translation_service import extract_code_blocks

        markdown: str = "Before\n\n```python\nx = 1\n```\n\nAfter"
        prose, blocks = extract_code_blocks(markdown)

        assert "Before" in prose
        assert "After" in prose


class TestTranslateToUrdu:
    """Tests for translate_to_urdu() async function."""

    @pytest.mark.asyncio
    async def test_returns_translated_content_and_blocks(self) -> None:
        """translate_to_urdu returns dict with translated_content and original_code_blocks."""
        from services.translation_service import translate_to_urdu

        markdown: str = (
            "# Gazebo Basics\n\nGazebo is a simulator.\n\n"
            "```python\nimport rclpy\n```\n\nMore content here."
        )

        with patch(
            "services.translation_service._call_gemini_translate",
            new_callable=AsyncMock,
            return_value="# گیزبو کی بنیادیں\n\nگیزبو ایک سمیولیٹر ہے۔\n\n{{CODE_BLOCK_0}}\n\nمزید مواد یہاں۔",
        ):
            result: dict = await translate_to_urdu(markdown)

        assert "translated_content" in result
        assert "original_code_blocks" in result
        assert isinstance(result["translated_content"], str)
        assert isinstance(result["original_code_blocks"], list)

    @pytest.mark.asyncio
    async def test_code_blocks_preserved_in_output(self) -> None:
        """Original code blocks appear unchanged in the translated content."""
        from services.translation_service import translate_to_urdu

        code_block: str = "```python\nimport rclpy\nfrom rclpy.node import Node\n```"
        markdown: str = f"# Test\n\nSome text.\n\n{code_block}\n\nEnd."

        with patch(
            "services.translation_service._call_gemini_translate",
            new_callable=AsyncMock,
            return_value="# ٹیسٹ\n\nکچھ متن۔\n\n{{CODE_BLOCK_0}}\n\nاختتام۔",
        ):
            result: dict = await translate_to_urdu(markdown)

        assert code_block in result["translated_content"]
        assert code_block in result["original_code_blocks"]

    @pytest.mark.asyncio
    async def test_multiple_blocks_reinsertion(self) -> None:
        """Multiple code blocks are all re-inserted at correct positions."""
        from services.translation_service import translate_to_urdu

        block_a: str = "```python\na = 1\n```"
        block_b: str = "```bash\necho hello\n```"
        markdown: str = f"Start\n\n{block_a}\n\nMiddle\n\n{block_b}\n\nEnd"

        with patch(
            "services.translation_service._call_gemini_translate",
            new_callable=AsyncMock,
            return_value="شروع\n\n{{CODE_BLOCK_0}}\n\nدرمیان\n\n{{CODE_BLOCK_1}}\n\nاختتام",
        ):
            result: dict = await translate_to_urdu(markdown)

        assert block_a in result["translated_content"]
        assert block_b in result["translated_content"]
        assert len(result["original_code_blocks"]) == 2
