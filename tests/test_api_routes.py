"""
Unit tests for SkillSync Flask Routes & API Contracts.

Tests /api/health, /analyze-skills, /analyze-resume, and /courses.
"""

import io
import unittest
from unittest.mock import patch
from app import app


class TestAPIRoutes(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_health_check_endpoint(self):
        """Test GET /api/health returns healthy status."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "SkillSync")
        self.assertIn("ai_provider", data)
        self.assertIn("taxonomy_skills_count", data)

    def test_analyze_skills_endpoint_success(self):
        """Test POST /analyze-skills with valid input."""
        res = self.client.post("/analyze-skills", json={"skills": "Python, Flask, SQL"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("user_skills", data)
        self.assertIn("competency_level", data)
        self.assertIn("job_match_score", data)
        self.assertIn("best_matching_role", data)

    def test_analyze_skills_empty_input(self):
        """Test POST /analyze-skills with empty input returns 400."""
        res = self.client.post("/analyze-skills", json={"skills": "   "})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "EMPTY_SKILLS")

    def test_analyze_resume_missing_file(self):
        """Test POST /analyze-resume missing file returns 400."""
        res = self.client.post(
            "/analyze-resume",
            data={"job_description": "We need Python"},
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "MISSING_RESUME_FILE")

    def test_analyze_resume_missing_job(self):
        """Test POST /analyze-resume missing job description returns 400."""
        resume_data = io.BytesIO(b"Python developer")
        res = self.client.post(
            "/analyze-resume",
            data={"resume": (resume_data, "resume.txt"), "job_description": ""},
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "MISSING_JOB_DESCRIPTION")

    def test_analyze_resume_unsupported_file_format(self):
        """Test POST /analyze-resume with unsupported file returns 400."""
        resume_data = io.BytesIO(b"binary data")
        res = self.client.post(
            "/analyze-resume",
            data={"resume": (resume_data, "resume.exe"), "job_description": "Job text"},
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "UNSUPPORTED_FILE_TYPE")

    @patch("backend.services.ai_service.AIService.provider")
    def test_analyze_resume_provider_unavailable_returns_503(self, mock_provider_prop):
        """When AI provider is unconfigured, /analyze-resume returns 503 per Section 18."""
        mock_provider = unittest.mock.MagicMock()
        mock_provider.is_available.return_value = (False, "API key missing")
        mock_provider_prop.__get__ = unittest.mock.MagicMock(return_value=mock_provider)

        resume_data = io.BytesIO(b"Python developer")
        res = self.client.post(
            "/analyze-resume",
            data={"resume": (resume_data, "resume.txt"), "job_description": "We need a Python dev"},
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 503)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "AI_PROVIDER_UNAVAILABLE")

    @patch("backend.services.ai_service.AIService.analyze_job_description")
    @patch("backend.services.ai_service.AIService.analyze_resume")
    @patch("backend.services.ai_service.AIService.provider")
    def test_analyze_resume_success_flow(self, mock_provider_prop, mock_analyze_resume, mock_analyze_job):
        """When AI provider is available, /analyze-resume succeeds with structured results."""
        mock_provider = unittest.mock.MagicMock()
        mock_provider.is_available.return_value = (True, "Ready")
        mock_provider_prop.__get__ = unittest.mock.MagicMock(return_value=mock_provider)

        mock_analyze_resume.return_value = {
            "candidate_name": "Arzoo Dahiya",
            "skills": ["Python", "Flask", "SQL"],
        }
        mock_analyze_job.return_value = {
            "role": "Backend Engineer",
            "required_skills": ["Python", "Docker"],
            "preferred_skills": ["SQL"],
        }

        resume_data = io.BytesIO(b"Candidate resume content with Python and Flask")
        res = self.client.post(
            "/analyze-resume",
            data={"resume": (resume_data, "resume.txt"), "job_description": "Looking for Backend Engineer"},
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("match_score", data)
        self.assertIn("Python", data["matched_skills"])
        self.assertIn("Docker", data["missing_skills"])

    def test_courses_endpoint(self):
        """Test GET /courses endpoint returns verified curated learning resources."""
        res = self.client.get("/courses")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)
        self.assertIn("courses", data)

    def test_courses_endpoint_skill_filter(self):
        """Test GET /courses?skill=Python filters courses."""
        res = self.client.get("/courses?skill=Python")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)
        for c in data["courses"]:
            skills = [s.lower() for s in c["skills_covered"]]
            self.assertIn("python", skills)


if __name__ == "__main__":
    unittest.main()
