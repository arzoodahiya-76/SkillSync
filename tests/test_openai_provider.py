"""
Unit tests for OpenAIProvider.

Tests configuration, availability detection, and mock response parsing
without requiring an active OpenAI key.
"""

import unittest
from unittest.mock import MagicMock, patch
from backend.providers.openai_provider import OpenAIProvider
from backend.providers.base import AIProviderError


class TestOpenAIProvider(unittest.TestCase):

    def test_provider_name(self):
        """Test provider name property."""
        provider = OpenAIProvider(api_key="test_key")
        self.assertEqual(provider.provider_name, "openai")

    def test_availability_unconfigured(self):
        """Ensure provider reports unavailable when api_key is empty."""
        provider = OpenAIProvider(api_key="")
        available, reason = provider.is_available()
        self.assertFalse(available)
        self.assertIn("not configured", reason)

    def test_unconfigured_call_raises_error(self):
        """Calling generation when unconfigured raises clear AIProviderError."""
        provider = OpenAIProvider(api_key="")
        with self.assertRaises(AIProviderError) as ctx:
            provider.analyze_skills("Python")
        self.assertEqual(ctx.exception.code, "OPENAI_NOT_CONFIGURED")

    @patch("backend.providers.openai_provider.OpenAIProvider._get_client")
    def test_mock_generate_json(self, mock_get_client):
        """Test that structured JSON from OpenAI client is properly parsed."""
        mock_choice = MagicMock()
        mock_choice.message.content = '{"extracted_skills": ["SQL", "Python"], "suggested_role": "Data Analyst"}'

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = OpenAIProvider(api_key="dummy_key")
        result = provider.analyze_skills("SQL and Python")

        self.assertIn("extracted_skills", result)
        self.assertEqual(result["extracted_skills"], ["SQL", "Python"])
        self.assertEqual(result["suggested_role"], "Data Analyst")


if __name__ == "__main__":
    unittest.main()
