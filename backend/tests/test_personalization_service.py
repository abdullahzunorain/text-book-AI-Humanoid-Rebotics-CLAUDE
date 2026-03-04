"""
Unit tests for personalization service — prompt building and chapter personalization.

TDD: These tests are written first and MUST FAIL until the service is implemented (E2).

Tests cover:
- build_personalization_prompt() includes all 5 profile fields and chapter content
- personalize_chapter() returns {"personalized_content": str}
- Missing background fields default to beginner values (FR-037)
- Returned content preserves code blocks from original (FR-033)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Default profile used throughout tests
# ---------------------------------------------------------------------------

_FULL_PROFILE: dict[str, str | bool] = {
    "python_level": "intermediate",
    "robotics_experience": "student",
    "math_level": "undergraduate",
    "hardware_access": True,
    "learning_goal": "Build a humanoid robot",
}

_CHAPTER_MD: str = (
    "# Forward Kinematics\n\n"
    "Forward kinematics computes end-effector pose.\n\n"
    "```python\nimport numpy as np\n```\n\n"
    "More explanation here."
)


class TestBuildPersonalizationPrompt:
    """Tests for build_personalization_prompt() helper."""

    def test_prompt_contains_all_five_profile_fields(self) -> None:
        """The generated prompt must include every profile field value."""
        from services.personalization_service import build_personalization_prompt

        prompt: str = build_personalization_prompt(_CHAPTER_MD, _FULL_PROFILE)

        assert "intermediate" in prompt  # python_level
        assert "student" in prompt  # robotics_experience
        assert "undergraduate" in prompt  # math_level
        assert "True" in prompt or "true" in prompt.lower()  # hardware_access
        assert "Build a humanoid robot" in prompt  # learning_goal

    def test_prompt_contains_chapter_content(self) -> None:
        """Chapter markdown (or its prose) must appear in the prompt."""
        from services.personalization_service import build_personalization_prompt

        prompt: str = build_personalization_prompt(_CHAPTER_MD, _FULL_PROFILE)

        assert "Forward Kinematics" in prompt
        assert "end-effector pose" in prompt

    def test_prompt_instructs_code_preservation(self) -> None:
        """Prompt must contain instructions to keep code blocks unchanged (FR-033)."""
        from services.personalization_service import build_personalization_prompt

        prompt: str = build_personalization_prompt(_CHAPTER_MD, _FULL_PROFILE)

        # Must mention preserving / keeping code blocks as-is
        prompt_lower: str = prompt.lower()
        assert "code" in prompt_lower
        assert any(
            kw in prompt_lower
            for kw in ("unchanged", "preserve", "do not modify", "as-is", "keep")
        )

    def test_missing_fields_use_beginner_defaults(self) -> None:
        """When profile fields are missing, defaults from FR-037 are applied."""
        from services.personalization_service import build_personalization_prompt

        empty_profile: dict[str, str | bool] = {}
        prompt: str = build_personalization_prompt(_CHAPTER_MD, empty_profile)

        # Defaults: beginner, none, high_school, False, ""
        assert "beginner" in prompt
        assert "none" in prompt
        assert "high_school" in prompt

    def test_partial_profile_fills_missing_with_defaults(self) -> None:
        """Partially filled profile keeps provided values and defaults the rest."""
        from services.personalization_service import build_personalization_prompt

        partial: dict[str, str | bool] = {
            "python_level": "advanced",
            "hardware_access": True,
        }
        prompt: str = build_personalization_prompt(_CHAPTER_MD, partial)

        assert "advanced" in prompt  # provided
        assert "none" in prompt  # default robotics_experience
        assert "high_school" in prompt  # default math_level


class TestPersonalizeChapter:
    """Tests for personalize_chapter() async function."""

    @pytest.mark.asyncio
    async def test_returns_personalized_content(self) -> None:
        """personalize_chapter returns dict with 'personalized_content' string."""
        from services.personalization_service import personalize_chapter

        mock_pool = MagicMock()
        mock_pool.fetchrow = AsyncMock(
            return_value={
                "python_level": "intermediate",
                "robotics_experience": "student",
                "math_level": "undergraduate",
                "hardware_access": True,
                "learning_goal": "Build a humanoid robot",
            }
        )

        gemini_response: str = (
            "# Forward Kinematics\n\n"
            "Since you have student-level robotics experience, "
            "let me focus on the practical aspects.\n\n"
            "```python\nimport numpy as np\n```\n\n"
            "More adapted explanation."
        )

        with (
            patch("services.personalization_service.get_pool", return_value=mock_pool),
            patch(
                "services.personalization_service._call_gemini_personalize",
                new_callable=AsyncMock,
                return_value=gemini_response,
            ),
            patch(
                "builtins.open",
                MagicMock(
                    return_value=MagicMock(
                        __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=_CHAPTER_MD))),
                        __exit__=MagicMock(return_value=False),
                    )
                ),
            ),
        ):
            result: dict[str, str] = await personalize_chapter(
                chapter_slug="module-1/forward-kinematics", user_id=1
            )

        assert "personalized_content" in result
        assert isinstance(result["personalized_content"], str)
        assert len(result["personalized_content"]) > 0

    @pytest.mark.asyncio
    async def test_preserves_code_blocks(self) -> None:
        """Code blocks from original chapter appear unchanged in output (FR-033)."""
        from services.personalization_service import personalize_chapter

        mock_pool = MagicMock()
        mock_pool.fetchrow = AsyncMock(return_value=dict(_FULL_PROFILE))

        # Gemini returns personalized text with placeholder re-inserted
        gemini_response: str = (
            "# Forward Kinematics\n\n"
            "Adapted prose.\n\n"
            "{{CODE_BLOCK_0}}\n\n"
            "More adapted text."
        )

        with (
            patch("services.personalization_service.get_pool", return_value=mock_pool),
            patch(
                "services.personalization_service._call_gemini_personalize",
                new_callable=AsyncMock,
                return_value=gemini_response,
            ),
            patch(
                "builtins.open",
                MagicMock(
                    return_value=MagicMock(
                        __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=_CHAPTER_MD))),
                        __exit__=MagicMock(return_value=False),
                    )
                ),
            ),
        ):
            result: dict[str, str] = await personalize_chapter(
                chapter_slug="module-1/forward-kinematics", user_id=1
            )

        # Original code block must be present
        assert "```python\nimport numpy as np\n```" in result["personalized_content"]

    @pytest.mark.asyncio
    async def test_missing_background_uses_defaults(self) -> None:
        """When user has no saved background, defaults are used (FR-037)."""
        from services.personalization_service import personalize_chapter

        mock_pool = MagicMock()
        # fetchrow returns None — no background saved
        mock_pool.fetchrow = AsyncMock(return_value=None)

        gemini_response: str = "Beginner-friendly explanation.\n\n{{CODE_BLOCK_0}}"

        with (
            patch("services.personalization_service.get_pool", return_value=mock_pool),
            patch(
                "services.personalization_service._call_gemini_personalize",
                new_callable=AsyncMock,
                return_value=gemini_response,
            ),
            patch(
                "builtins.open",
                MagicMock(
                    return_value=MagicMock(
                        __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=_CHAPTER_MD))),
                        __exit__=MagicMock(return_value=False),
                    )
                ),
            ),
        ):
            result: dict[str, str] = await personalize_chapter(
                chapter_slug="module-1/forward-kinematics", user_id=99
            )

        assert "personalized_content" in result
