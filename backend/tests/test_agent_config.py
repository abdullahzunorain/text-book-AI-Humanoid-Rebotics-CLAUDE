"""
Unit tests for services/agent_config.py — agent infrastructure.

Tests cover:
- Shared client creation with correct base_url and api_key
- All 3 agents exist with correct names
- run_agent() calls Runner.run() and returns final_output
- embed() calls client.embeddings.create() and returns list of floats
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAgentInstances:
    """Verify that all three agents are correctly configured."""

    def test_tutor_agent_exists(self) -> None:
        from services.agent_config import tutor_agent
        assert tutor_agent.name == "tutor"
        assert "Physical AI" in tutor_agent.instructions

    def test_personalization_agent_exists(self) -> None:
        from services.agent_config import personalization_agent
        assert personalization_agent.name == "personalizer"
        assert "tutor" in personalization_agent.instructions.lower() or "adapt" in personalization_agent.instructions.lower()

    def test_translation_agent_exists(self) -> None:
        from services.agent_config import translation_agent
        assert translation_agent.name == "translator"
        assert "urdu" in translation_agent.instructions.lower() or "translator" in translation_agent.instructions.lower()


class TestSharedClient:
    """Verify the shared AsyncOpenAI client configuration."""

    def test_client_base_url(self) -> None:
        from services.agent_config import _client
        assert "generativelanguage.googleapis.com" in str(_client.base_url)

    def test_model_name(self) -> None:
        from services.agent_config import GENERATION_MODEL
        assert "gemini" in GENERATION_MODEL


class TestRunAgent:
    """Tests for the run_agent() helper."""

    @pytest.mark.asyncio
    async def test_run_agent_returns_final_output(self) -> None:
        from services.agent_config import run_agent, tutor_agent

        mock_result = MagicMock()
        mock_result.final_output = "This is the answer about ROS 2."

        with patch("services.agent_config.Runner.run", new_callable=AsyncMock, return_value=mock_result):
            output = await run_agent(tutor_agent, input="What is ROS 2?")

        assert output == "This is the answer about ROS 2."

    @pytest.mark.asyncio
    async def test_run_agent_calls_runner(self) -> None:
        from services.agent_config import run_agent, tutor_agent

        mock_result = MagicMock()
        mock_result.final_output = "Answer"

        with patch("services.agent_config.Runner.run", new_callable=AsyncMock, return_value=mock_result) as mock_run:
            await run_agent(tutor_agent, input="test")

        mock_run.assert_called_once_with(tutor_agent, input="test")


class TestEmbed:
    """Tests for the embed() helper."""

    @pytest.mark.asyncio
    async def test_embed_returns_list_of_floats(self) -> None:
        from services.agent_config import embed

        mock_embedding = MagicMock()
        mock_embedding.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]

        with patch("services.agent_config._client") as mock_client:
            mock_client.embeddings.create = AsyncMock(return_value=mock_embedding)
            result = await embed("Hello world")

        assert result == [0.1, 0.2, 0.3]
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_embed_calls_correct_model(self) -> None:
        from services.agent_config import embed, EMBEDDING_MODEL

        mock_embedding = MagicMock()
        mock_embedding.data = [MagicMock(embedding=[0.5])]

        with patch("services.agent_config._client") as mock_client:
            mock_client.embeddings.create = AsyncMock(return_value=mock_embedding)
            await embed("test text")

        mock_client.embeddings.create.assert_called_once_with(
            input="test text",
            model=EMBEDDING_MODEL,
        )
