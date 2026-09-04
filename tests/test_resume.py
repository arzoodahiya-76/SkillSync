"""
Unit tests for Resume and Job Description Competency Evaluation.

Verifies deterministic matching, evidence recording, and scoring.
"""

import unittest
from backend.competency_engine import get_competency_engine


class TestResumeEvaluation(unittest.TestCase):

    def setUp(self):
        self.engine = get_competency_engine()

    def test_evaluate_resume_and_job_matching(self):
        """Test deterministic matching between extracted resume data and job requirements."""
        resume_data = {
            "candidate_name": "Arzoo Dahiya",
            "skills": ["Python", "Flask", "SQL", "Git"],
        }
        job_data = {
            "role": "Backend Python Engineer",
            "required_skills": ["Python", "Flask", "Docker"],
            "preferred_skills": ["AWS", "SQL"],
        }

        result = self.engine.evaluate_resume_and_job(resume_data, job_data)

        self.assertTrue(result["success"])
        self.assertIn("Python", result["matched_skills"])
        self.assertIn("Flask", result["matched_skills"])
        self.assertIn("SQL", result["matched_skills"])
        self.assertIn("Docker", result["missing_skills"])
        self.assertGreater(result["match_score"], 40)
        self.assertLessEqual(result["match_score"], 100)

        # Check evidence records
        evidence = result["evidence_records"]
        self.assertGreater(len(evidence), 0)
        first_evidence = evidence[0]
        self.assertEqual(first_evidence["evidence_type"], "RESUME")
        self.assertLessEqual(first_evidence["confidence"], 0.35)

    def test_evaluate_resume_fallback_text_extraction(self):
        """Ensure fallback keyword scanning works if structured skills are empty."""
        raw_resume = "Experienced software developer skilled in Python, JavaScript, and HTML."
        raw_job = "We are seeking a developer proficient in Python and React."

        result = self.engine.evaluate_resume_and_job(
            resume_data={},
            job_data={},
            raw_resume_text=raw_resume,
            raw_job_text=raw_job,
        )

        self.assertTrue(result["success"])
        self.assertIn("Python", result["matched_skills"])
        self.assertIn("React", result["missing_skills"])


if __name__ == "__main__":
    unittest.main()
