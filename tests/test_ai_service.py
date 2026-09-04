"""
Unit tests for AIService and Provider Abstraction.

Tests provider selection, data normalization, and mock provider handling.
Does NOT require live API keys.
"""

import unittest
from unittest.mock import MagicMock
from backend.services.ai_service import AIService
from backend.providers.base import AIProvider, AIProviderError


class MockProvider(AIProvider):
    """Mock implementation of AIProvider for deterministic unit testing."""

    @property
    def provider_name(self) -> str:
        return "mock"

    def is_available(self) -> tuple[bool, str]:
        return True, "Mock Ready"

    def analyze_skills(self, user_input: str, context=None):
        return {
            "extracted_skills": ["python", "reactjs", "SQL"],
            "domain_focus": "Full Stack",
            "suggested_role": "Software Engineer",
            "suggested_competency_level": "Intermediate",
            "strengths": ["python", "SQL"],
            "missing_skills": ["docker"],
            "recommended_skills": ["docker", "kubernetes"],
            "summary": "Solid foundation in full stack development.",
        }

    def analyze_resume(self, resume_text: str, context=None):
        return {
            "candidate_name": "Test Candidate",
            "current_title": "Junior Developer",
            "skills": ["python", "flask", "git"],
            "experience_years_estimate": 2,
            "experience_summary": "Two years of backend development.",
            "strengths": ["REST API development"],
            "projects": ["SkillSync"],
            "education": ["BS Computer Science"],
        }

    def analyze_job_description(self, job_text: str, context=None):
        return {
            "role": "Backend Engineer",
            "company": "Tech Corp",
            "required_skills": ["python", "flask", "docker"],
            "preferred_skills": ["kubernetes", "aws"],
            "competency_expectations": [],
            "responsibilities": ["Build backend services"],
        }

    def generate_interview_questions(self, role: str, skills: list, context=None):
        return [{"id": 1, "skill": "Python", "question": "Explain generators."}]

    def evaluate_interview_response(self, question: str, response_text: str, context=None):
        return {"score": 85, "feedback": "Good answer"}

    def analyze_project(self, project_description: str, repo_url=None, context=None):
        return {"applied_skills": ["Python"]}


class TestAIService(unittest.TestCase):

    def setUp(self):
        self.mock_provider = MockProvider()
        self.service = AIService(provider=self.mock_provider)

    def test_provider_status(self):
        """Test that get_status reports mock provider readiness."""
        status = self.service.get_status()
        self.assertEqual(status["active_provider"], "mock")
        self.assertTrue(status["available"])

    def test_analyze_skills_normalization(self):
        """Ensure skills extracted by AI are normalized against canonical taxonomy."""
        result = self.service.analyze_skills("Python and React")
        self.assertEqual(result["provider"], "mock")
        # 'python' normalized to 'Python', 'reactjs' normalized to 'React'
        self.assertIn("Python", result["extracted_skills"])
        self.assertIn("React", result["extracted_skills"])
        self.assertIn("SQL", result["extracted_skills"])

    def test_analyze_skills_empty_input(self):
        """Ensure empty input raises ValueError before calling provider."""
        with self.assertRaises(ValueError):
            self.service.analyze_skills("   ")

    def test_analyze_resume_normalization(self):
        """Ensure resume extraction produces normalized skills."""
        result = self.service.analyze_resume("Resume content here")
        self.assertEqual(result["candidate_name"], "Test Candidate")
        self.assertIn("Python", result["skills"])
        self.assertIn("Flask", result["skills"])
        self.assertIn("Git", result["skills"])

    def test_unsupported_provider_error(self):
        """Ensure configuring an unknown provider raises a clear AIProviderError."""
        bad_service = AIService(provider_name="unknown_llm")
        with self.assertRaises(AIProviderError) as ctx:
            _ = bad_service.provider
        self.assertEqual(ctx.exception.code, "UNSUPPORTED_PROVIDER")


if __name__ == "__main__":
    unittest.main()
