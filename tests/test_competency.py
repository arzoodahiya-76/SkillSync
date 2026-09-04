"""
Unit tests for SkillSync Deterministic Competency Engine & Taxonomy.

Runs 100% offline with zero dependencies on API keys or external network.
"""

import unittest
from backend.competency_engine import get_competency_engine, CompetencyEngine
from backend.taxonomy import get_taxonomy, SkillTaxonomy
from backend.models.evidence import EvidenceRecord, EvidenceType, VerificationStatus


class TestDeterministicCompetencyEngine(unittest.TestCase):

    def setUp(self):
        self.engine = get_competency_engine()
        self.taxonomy = get_taxonomy()

    def test_taxonomy_normalization(self):
        """Test that synonyms and lowercase strings map to canonical taxonomy skills."""
        self.assertEqual(self.taxonomy.normalize("py"), "Python")
        self.assertEqual(self.taxonomy.normalize("python"), "Python")
        self.assertEqual(self.taxonomy.normalize("reactjs"), "React")
        self.assertEqual(self.taxonomy.normalize("js"), "JavaScript")
        self.assertEqual(self.taxonomy.normalize("dsa"), "Data Structures")

    def test_normalize_skills_list(self):
        """Test skill normalization with comma-separated and list inputs."""
        skills_str = "python, ReactJS, js, SQL, unknown_new_skill"
        normalized = self.engine.normalize_skills(skills_str)
        self.assertIn("Python", normalized)
        self.assertIn("React", normalized)
        self.assertIn("JavaScript", normalized)
        self.assertIn("SQL", normalized)
        self.assertIn("Unknown_New_Skill", normalized)

    def test_categorize_skills(self):
        """Test skill categorization into taxonomy domains."""
        skills = ["Python", "JavaScript", "SQL", "Docker"]
        categories = self.engine.categorize_skills(skills)
        self.assertIn("Software Development", categories)
        self.assertIn("Web Development", categories)
        self.assertIn("Data Management", categories)
        self.assertIn("DevOps & Tools", categories)

    def test_infer_best_matching_role(self):
        """Test deterministic role matching based on skill overlap."""
        web_skills = ["JavaScript", "HTML", "CSS", "React", "Node.js"]
        role, score = self.engine.infer_best_matching_role(web_skills)
        self.assertEqual(role, "Full Stack Web Developer")
        self.assertGreater(score, 50.0)

    def test_proficiency_calculation_breadth(self):
        """Test proficiency level scoring with different skill breadths."""
        beginner_skills = ["HTML"]
        level, score = self.engine.calculate_proficiency(beginner_skills)
        self.assertEqual(level, "Beginner")

        advanced_skills = ["Python", "Flask", "SQL", "Docker", "Git", "Kubernetes", "AWS", "Data Structures"]
        level_adv, score_adv = self.engine.calculate_proficiency(advanced_skills)
        self.assertIn(level_adv, ["Intermediate", "Advanced"])
        self.assertGreater(score_adv, score)

    def test_evidence_weighting_ceiling(self):
        """Ensure a single resume or self-claim cannot alone award maximum mastery."""
        resume_record = EvidenceRecord(
            competency="Python",
            evidence_type=EvidenceType.RESUME,
            confidence=1.0,  # Requesting full confidence
            verification_status=VerificationStatus.UNVERIFIED,
        )
        # Should be capped by base ceiling
        self.assertLessEqual(resume_record.confidence, 0.35)

    def test_evaluate_skills_profile_deterministic(self):
        """Test complete profile evaluation purely through deterministic logic."""
        result = self.engine.evaluate_skills_profile("Python, Flask, SQL, Git")
        self.assertTrue(result["success"])
        self.assertIn("user_skills", result)
        self.assertIn("competency_level", result)
        self.assertIn("job_match_score", result)
        self.assertIn("best_matching_role", result)
        self.assertIn("recommended_skills", result)
        self.assertIn("missing_skills", result)
        self.assertIn("domain_distribution", result)

    def test_evaluate_skills_profile_empty(self):
        """Test handling of empty skills input."""
        result = self.engine.evaluate_skills_profile("")
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()
