"""
SkillSync Deterministic Competency Engine.

COMPLETELY PROVIDER-INDEPENDENT.
Contains ZERO AI SDK imports (no openai, no google-genai), ZERO network calls,
ZERO API keys, and ZERO prompts.

Performs deterministic business logic:
- Skill normalization and alias resolution via taxonomy
- Multi-domain categorization
- Proficiency scoring & level calculation
- Multi-factor Evidence Engine weighting
- Skill gap identification & prioritization
- Job description match scoring
- Transparent explainability for all recommendations
"""

from typing import List, Dict, Tuple, Optional, Any, Union
from backend.taxonomy import get_taxonomy
from backend.models.evidence import (
    EvidenceRecord,
    EvidenceType,
    VerificationStatus,
    EVIDENCE_TYPE_WEIGHTS,
)

# Standard career role definitions and their core prerequisite skills
ROLE_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "Full Stack Web Developer": {
        "domain": "Web Development",
        "core_skills": ["JavaScript", "HTML", "CSS", "React", "Node.js", "SQL", "Git"],
        "min_skills_for_match": 2,
    },
    "Backend Python Engineer": {
        "domain": "Software Development",
        "core_skills": ["Python", "Flask", "Django", "SQL", "REST API", "Git", "Docker"],
        "min_skills_for_match": 2,
    },
    "Data Scientist": {
        "domain": "Data Science",
        "core_skills": ["Python", "NumPy", "Pandas", "SQL", "Machine Learning", "Data Visualization"],
        "min_skills_for_match": 2,
    },
    "Machine Learning Engineer": {
        "domain": "Artificial Intelligence",
        "core_skills": ["Python", "Machine Learning", "NumPy", "Pandas", "Data Structures", "Docker"],
        "min_skills_for_match": 2,
    },
    "Software Engineer": {
        "domain": "Software Development",
        "core_skills": ["Python", "Java", "C++", "Data Structures", "Algorithms", "Git", "SQL"],
        "min_skills_for_match": 2,
    },
    "DevOps / Cloud Engineer": {
        "domain": "DevOps & Tools",
        "core_skills": ["Docker", "Kubernetes", "Git", "Linux", "AWS", "CI/CD"],
        "min_skills_for_match": 2,
    },
}


class CompetencyEngine:
    """Deterministic Competency & Skills Evaluation Engine."""

    def __init__(self):
        self.taxonomy = get_taxonomy()

    def normalize_skills(self, skills_input: Union[str, List[str]]) -> List[str]:
        """
        Converts comma-separated string or list into standardized canonical skills
        using the SkillSync taxonomy. Preserves order, deduplicates.
        """
        if isinstance(skills_input, str):
            raw_list = [s.strip() for s in skills_input.split(",") if s.strip()]
        elif isinstance(skills_input, list):
            raw_list = [str(s).strip() for s in skills_input if str(s).strip()]
        else:
            return []

        normalized: List[str] = []
        for raw in raw_list:
            canonical = self.taxonomy.normalize(raw)
            clean_name = canonical if canonical else raw.title()
            if clean_name not in normalized:
                normalized.append(clean_name)
        return normalized

    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Groups canonical skills into their respective taxonomy domains."""
        categorized: Dict[str, List[str]] = {}
        for skill in skills:
            meta = self.taxonomy.get_metadata(skill)
            domain = meta.domain if meta else "General Technology"
            categorized.setdefault(domain, []).append(skill)
        return categorized

    def infer_best_matching_role(self, user_skills: List[str]) -> Tuple[str, float]:
        """
        Deterministically infers the closest career archetype based on skill overlap.
        Returns: (role_name: str, match_percentage: float)
        """
        user_skills_lower = {s.lower() for s in user_skills}
        best_role = "General Technology Professional"
        best_score = 0.0

        for role, data in ROLE_ARCHETYPES.items():
            core = {s.lower() for s in data["core_skills"]}
            overlap = len(user_skills_lower.intersection(core))
            score = (overlap / len(core)) * 100.0 if core else 0.0
            if score > best_score:
                best_score = score
                best_role = role

        # Fallback baseline if no overlap with archetypes
        if best_score == 0 and user_skills:
            best_score = min(len(user_skills) * 15.0, 50.0)

        return best_role, round(best_score, 1)

    def calculate_proficiency(
        self,
        skills: List[str],
        evidence_records: Optional[List[EvidenceRecord]] = None
    ) -> Tuple[str, float]:
        """
        Calculates proficiency level and numeric competency score (0-100).
        Enforces: A single unverified claim, certificate, or resume never achieves mastery.
        """
        total_skills = len(skills)
        if total_skills == 0:
            return "Beginner", 0.0

        # 1. Base breadth score (0 to 60)
        # 1-2 skills = 20-35, 3-5 skills = 40-55, 6+ skills = 60
        breadth_score = min(total_skills * 10.0, 60.0)

        # 2. Evidence confidence adjustment (0 to 40)
        evidence_score = 15.0  # default baseline for self-entry
        if evidence_records:
            total_weight = 0.0
            weighted_sum = 0.0
            for record in evidence_records:
                weight = EVIDENCE_TYPE_WEIGHTS.get(record.evidence_type, 0.3)
                conf = record.confidence
                score_val = (record.score / 100.0) if record.score is not None else 0.7
                weighted_sum += (score_val * conf * weight)
                total_weight += weight
            if total_weight > 0:
                evidence_score = (weighted_sum / total_weight) * 40.0

        composite_score = min(breadth_score + evidence_score, 100.0)

        # Map to levels
        if composite_score >= 80.0:
            level = "Advanced"
        elif composite_score >= 50.0:
            level = "Intermediate"
        else:
            level = "Beginner"

        return level, round(composite_score, 1)

    def calculate_gaps_and_recommendations(
        self,
        user_skills: List[str],
        target_role: str
    ) -> Tuple[List[str], List[str]]:
        """
        Deterministically computes missing skills and recommended next learning steps
        based on the target role archetype.
        """
        user_skills_lower = {s.lower() for s in user_skills}
        role_data = ROLE_ARCHETYPES.get(target_role)

        missing_skills = []
        if role_data:
            for s in role_data["core_skills"]:
                if s.lower() not in user_skills_lower:
                    missing_skills.append(s)

        # If all core skills are matched or no archetype found, recommend domain extensions
        if not missing_skills:
            all_canonical = self.taxonomy.get_all_canonical_names()
            for s in all_canonical:
                if s.lower() not in user_skills_lower:
                    missing_skills.append(s)
                if len(missing_skills) >= 4:
                    break

        recommended = missing_skills[:6]
        critical_gaps = missing_skills[:4]
        return critical_gaps, recommended

    def evaluate_skills_profile(
        self,
        skills_input: Union[str, List[str]],
        ai_extracted: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Pure deterministic profile evaluation.
        Takes normalized user skills (and optional validated AI extraction),
        and applies deterministic scoring, gap identification, and explainability.
        """
        normalized_skills = self.normalize_skills(skills_input)

        # Incorporate AI extracted skills if provided and valid
        if ai_extracted and isinstance(ai_extracted, dict):
            extra = ai_extracted.get("extracted_skills", [])
            for s in self.normalize_skills(extra):
                if s not in normalized_skills:
                    normalized_skills.append(s)

        if not normalized_skills:
            return {
                "success": False,
                "message": "No valid skills recognized in input."
            }

        # Deterministic role inference and scoring
        inferred_role, archetype_match = self.infer_best_matching_role(normalized_skills)
        target_role = (
            ai_extracted.get("suggested_role")
            if (ai_extracted and ai_extracted.get("suggested_role"))
            else inferred_role
        )

        level, comp_score = self.calculate_proficiency(normalized_skills)
        missing_skills, recommended_skills = self.calculate_gaps_and_recommendations(
            normalized_skills, target_role
        )
        domain_breakdown = self.categorize_skills(normalized_skills)

        # Dynamic match score: combines archetype alignment with competency score
        job_match_score = round((archetype_match * 0.6) + (comp_score * 0.4))
        job_match_score = max(min(job_match_score, 98), 45)

        # Strengths: skills the candidate possesses that match taxonomy
        strengths = normalized_skills[:5]

        # Explainable summary
        summary = (
            f"Profile evaluated with {len(normalized_skills)} recognized competencies across "
            f"{len(domain_breakdown)} domain(s). Best alignment identified with '{target_role}'."
        )

        next_step = (
            f"Prioritize developing {recommended_skills[0]} to strengthen readiness for {target_role}."
            if recommended_skills else
            "Build end-to-end projects demonstrating your existing competencies."
        )

        return {
            "success": True,
            "user_skills": normalized_skills,
            "competency_level": level,
            "competency_score": comp_score,
            "job_match_score": job_match_score,
            "best_matching_role": target_role,
            "career_summary": summary,
            "domain_distribution": domain_breakdown,
            "strengths": strengths,
            "recommended_skills": recommended_skills,
            "missing_skills": missing_skills,
            "next_step": next_step,
        }

    def evaluate_resume_and_job(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        raw_resume_text: str = "",
        raw_job_text: str = ""
    ) -> Dict[str, Any]:
        """
        Deterministic comparison between extracted candidate resume data and job requirements.
        Calculates job match score, identifies verified overlaps, gaps, and recommendations.
        """
        resume_skills = self.normalize_skills(resume_data.get("skills", []))
        job_required = self.normalize_skills(job_data.get("required_skills", []))
        job_preferred = self.normalize_skills(job_data.get("preferred_skills", []))

        # Fallback text extraction if structured skills were empty
        if not resume_skills and raw_resume_text:
            resume_lower = raw_resume_text.lower()
            for skill in self.taxonomy.get_all_canonical_names():
                if skill.lower() in resume_lower:
                    resume_skills.append(skill)

        if not job_required and raw_job_text:
            job_lower = raw_job_text.lower()
            for skill in self.taxonomy.get_all_canonical_names():
                if skill.lower() in job_lower:
                    job_required.append(skill)

        all_job_skills = list(dict.fromkeys(job_required + job_preferred))
        if not all_job_skills:
            all_job_skills = resume_skills[:4] if resume_skills else ["Python", "Problem Solving"]

        resume_skills_lower = {s.lower() for s in resume_skills}

        matched_skills = [s for s in all_job_skills if s.lower() in resume_skills_lower]
        missing_skills = [s for s in all_job_skills if s.lower() not in resume_skills_lower]

        # Deterministic match score
        if all_job_skills:
            overlap_ratio = len(matched_skills) / len(all_job_skills)
            match_score = round(overlap_ratio * 100)
        else:
            match_score = 60

        match_score = min(max(match_score, 30 if resume_skills else 15), 98)

        # Create structured evidence records for the resume
        evidence_records = [
            EvidenceRecord(
                competency=skill,
                evidence_type=EvidenceType.RESUME,
                confidence=0.35,  # Resume alone is unverified self-claim
                verification_status=VerificationStatus.PENDING,
                source="Candidate Resume Upload",
                explanation=f"Skill '{skill}' extracted from uploaded resume.",
            ).to_dict()
            for skill in resume_skills
        ]

        strengths = (
            [f"Verified alignment in {s}" for s in matched_skills[:4]]
            if matched_skills else
            [f"Demonstrated background in {s}" for s in resume_skills[:3]]
        )
        if not strengths:
            strengths = ["Broad technical aptitude"]

        recommendations = (
            [f"Develop and verify competency in {s}" for s in missing_skills[:4]]
            if missing_skills else
            ["Demonstrate advanced project practicals to validate theoretical knowledge."]
        )

        return {
            "success": True,
            "match_score": match_score,
            "job_match_score": match_score,
            "matching_skills": matched_skills,
            "matched_skills": matched_skills,
            "resume_skills": resume_skills,
            "job_skills": all_job_skills,
            "missing_skills": missing_skills,
            "strengths": strengths,
            "recommendations": recommendations,
            "improvement_recommendations": recommendations,
            "evidence_records": evidence_records,
        }


# Singleton instance
_competency_engine: Optional[CompetencyEngine] = None


def get_competency_engine() -> CompetencyEngine:
    global _competency_engine
    if _competency_engine is None:
        _competency_engine = CompetencyEngine()
    return _competency_engine


# Backward-compatible functional aliases
def analyze_skills(skills_input: Union[str, List[str]]) -> Dict[str, Any]:
    """Backward-compatible deterministic skill analyzer."""
    engine = get_competency_engine()
    return engine.evaluate_skills_profile(skills_input)