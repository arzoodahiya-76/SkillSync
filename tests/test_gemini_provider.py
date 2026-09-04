"""
Unit tests for GeminiProvider.

Tests configuration, availability detection, and mock response parsing
without requiring an actual live Gemini API key.
"""

import unittest
from unittest.mock import MagicMock, patch
from backend.providers.gemini_provider import GeminiProvider
from backend.providers.base import AIProviderError


class TestGeminiProvider(unittest.TestCase):

    def test_provider_name(self):
        """Test provider name property."""
        provider = GeminiProvider(api_key="test_key")
        self.assertEqual(provider.provider_name, "gemini")

    def test_availability_unconfigured(self):
        """Ensure provider reports unavailable when api_key is empty."""
        provider = GeminiProvider(api_key="")
        available, reason = provider.is_available()
        self.assertFalse(available)
        self.assertIn("not configured", reason)

    def test_availability_configured(self):
        """Ensure provider reports available when api_key is provided."""
        provider = GeminiProvider(api_key="valid_format_key")
        available, reason = provider.is_available()
        self.assertTrue(available)
        self.assertEqual(reason, "Ready")

    def test_unconfigured_call_raises_error(self):
        """Calling generation when unconfigured raises clear AIProviderError."""
        provider = GeminiProvider(api_key="")
        with self.assertRaises(AIProviderError) as ctx:
            provider.analyze_skills("Python")
        self.assertEqual(ctx.exception.code, "GEMINI_NOT_CONFIGURED")

    @patch("backend.providers.gemini_provider.GeminiProvider._get_client")
    def test_mock_generate_json(self, mock_get_client):
        """Test that structured JSON from Gemini client is properly parsed."""
        mock_response = MagicMock()
        mock_response.text = '{"extracted_skills": ["Python", "Flask"], "suggested_role": "Backend Dev"}'

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = GeminiProvider(api_key="dummy_key")
        result = provider.analyze_skills("Python and Flask")

        self.assertIn("extracted_skills", result)
        self.assertEqual(result["extracted_skills"], ["Python", "Flask"])
        self.assertEqual(result["suggested_role"], "Backend Dev")

    @patch("backend.providers.gemini_provider.GeminiProvider._get_client")
    def test_malformed_json_handling(self, mock_get_client):
        """Ensure non-JSON response raises MALFORMED_AI_RESPONSE."""
        mock_response = MagicMock()
        mock_response.text = "This is plain text not JSON"

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = GeminiProvider(api_key="dummy_key")
        with self.assertRaises(AIProviderError) as ctx:
            provider.analyze_skills("Python")
        self.assertEqual(ctx.exception.code, "MALFORMED_AI_RESPONSE")


if __name__ == "__main__":
    unittest.main()
