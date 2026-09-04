"""
SkillSync AI Service Layer.

Selects configured AIProvider (Gemini by default, or OpenAI),
validates inputs, sends structured requests, normalizes responses into
provider-independent data, and returns clean outputs to the rest of the application.
"""

from typing import Dict, List, Optional, Any
from backend.config import Config
from backend.providers.base import AIProvider, AIProviderError
from backend.providers.gemini_provider import GeminiProvider
from backend.providers.openai_provider import OpenAIProvider
from backend.taxonomy import get_taxonomy


class AIService:
    """Orchestrates AI providers and normalizes structured AI responses."""

    def __init__(self, provider: Optional[AIProvider] = None, provider_name: Optional[str] = None):
        self._provider = provider
        self._provider_name = (provider_name or Config.AI_PROVIDER).lower()
        self.taxonomy = get_taxonomy()

    @property
    def provider(self) -> AIProvider:
        """Lazily instantiates the configured AIProvider."""
        if self._provider is None:
            if self._provider_name == "gemini":
                self._provider = GeminiProvider()
            elif self._provider_name == "openai":
                self._provider = OpenAIProvider()
            else:
                raise AIProviderError(
                    code="UNSUPPORTED_PROVIDER",
                    message=f"Configured AI provider '{self._provider_name}' is not supported. Use 'gemini' or 'openai'.",
                )
        return self._provider

    def get_status(self) -> Dict[str, Any]:
        """Returns the status and health of the active AI provider."""
        try:
            prov = self.provider
            available, reason = prov.is_available()
            return {
                "active_provider": prov.provider_name,
                "available": available,
                "status": reason,
            }
        except Exception as e:
            return {
                "active_provider": self._provider_name,
                "available": False,
                "status": str(e),
            }

    def _normalize_skill_list(self, raw_skills: Any) -> List[str]:
        """Normalizes a list of skills using the SkillSync taxonomy."""
        if not isinstance(raw_skills, list):
            return []
        normalized = []
        for s in raw_skills:
            if not isinstance(s, str) or not s.strip():
                continue
            canonical = self.taxonomy.normalize(s)
            normalized.append(canonical if canonical else s.strip())
        # Deduplicate while preserving order
        return list(dict.fromkeys(normalized))

    def analyze_skills(self, user_input: str) -> Dict[str, Any]:
        """
        Extracts structured skill profile from student input via the active AI provider.
        Validates and normalizes output before returning.
        """
        if not user_input or not user_input.strip():
            raise ValueError("User input must not be empty.")

        raw_result = self.provider.analyze_skills(user_input)

        # Validate and normalize structure
        extracted_skills = self._normalize_skill_list(raw_result.get("extracted_skills", []))
        strengths = self._normalize_skill_list(raw_result.get("strengths", []))
        missing_skills = self._normalize_skill_list(raw_result.get("missing_skills", []))
        recommended_skills = self._normalize_skill_list(raw_result.get("recommended_skills", []))

        return {
            "provider": self.provider.provider_name,
            "extracted_skills": extracted_skills,
            "domain_focus": str(raw_result.get("domain_focus", "General Technology")),
            "suggested_role": str(raw_result.get("suggested_role", "Technology Specialist")),
            "suggested_competency_level": str(raw_result.get("suggested_competency_level", "Intermediate")),
            "strengths": strengths,
            "missing_skills": missing_skills,
            "recommended_skills": recommended_skills,
            "summary": str(raw_result.get("summary", "")),
        }

    def analyze_resume(self, resume_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extracts structured candidate data from resume text via active AI provider.
        """
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text must not be empty.")

        raw_result = self.provider.analyze_resume(resume_text, context)

        skills = self._normalize_skill_list(raw_result.get("skills", []))
        strengths = [str(s) for s in raw_result.get("strengths", []) if isinstance(s, str)]
        projects = [str(p) for p in raw_result.get("projects", []) if isinstance(p, str)]
        education = [str(e) for e in raw_result.get("education", []) if isinstance(e, str)]

        return {
            "provider": self.provider.provider_name,
            "candidate_name": raw_result.get("candidate_name"),
            "current_title": str(raw_result.get("current_title", "Technical Candidate")),
            "skills": skills,
            "experience_years_estimate": raw_result.get("experience_years_estimate", 1),
            "experience_summary": str(raw_result.get("experience_summary", "")),
            "strengths": strengths,
            "projects": projects,
            "education": education,
        }

    def analyze_job_description(self, job_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extracts structured job requirements and competencies from job description.
        """
        if not job_text or not job_text.strip():
            raise ValueError("Job text must not be empty.")

        raw_result = self.provider.analyze_job_description(job_text, context)

        required = self._normalize_skill_list(raw_result.get("required_skills", []))
        preferred = self._normalize_skill_list(raw_result.get("preferred_skills", []))
        responsibilities = [str(r) for r in raw_result.get("responsibilities", []) if isinstance(r, str)]

        return {
            "provider": self.provider.provider_name,
            "role": str(raw_result.get("role", "Software Role")),
            "company": raw_result.get("company"),
            "required_skills": required,
            "preferred_skills": preferred,
            "competency_expectations": raw_result.get("competency_expectations", []),
            "responsibilities": responsibilities,
        }
        
        
        def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
            """
        Generates natural-language text using the configured AI provider.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        return self.provider.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
        )
        
        def generate_follow_up_question(
        self,
        role: str,
        previous_question: str,
        response_text: str,
        evaluation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
            """
        Generates an adaptive follow-up interview question through
        the configured AI provider.
        """
        if not role or not role.strip():
            raise ValueError("Role must not be empty.")

        if not previous_question or not previous_question.strip():
            raise ValueError("Previous question must not be empty.")

        if not response_text or not response_text.strip():
            raise ValueError("Response text must not be empty.")

        return self.provider.generate_follow_up_question(
            role=role,
            previous_question=previous_question,
            response_text=response_text,
            evaluation=evaluation,
            context=context,
        )
# Global singleton instance helper
_ai_service_instance: Optional[AIService] = None


def get_ai_service(provider_name: Optional[str] = None) -> AIService:
    """Returns the AIService singleton or creates a new one if provider specified."""
    global _ai_service_instance
    if provider_name is not None:
        return AIService(provider_name=provider_name)
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
