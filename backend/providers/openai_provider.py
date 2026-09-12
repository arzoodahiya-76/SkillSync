"""
SkillSync OpenAI Provider (Optional Provider).

Implements AIProvider interface using OpenAI's Python SDK.
Configured dynamically via environment variables / Config.
Returns validated structured JSON output.
"""

import json
from typing import Dict, List, Optional, Any

from backend.config import Config
from backend.providers.base import AIProvider, AIProviderError


class OpenAIProvider(AIProvider):
    """Optional AI provider implementing the AIProvider interface."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        self._client = None

    @property
    def provider_name(self) -> str:
        return "openai"

    def is_available(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "OPENAI_API_KEY is not configured in environment."
        return True, "Ready"

    def _get_client(self):
        """Initializes the OpenAI client safely."""
        if self._client is None:
            available, reason = self.is_available()
            if not available:
                raise AIProviderError(
                    code="OPENAI_NOT_CONFIGURED",
                    message=f"OpenAI provider is not configured: {reason}",
                )
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise AIProviderError(
                    code="SDK_NOT_INSTALLED",
                    message="The openai SDK is not installed in the Python environment.",
                )
            except Exception as e:
                raise AIProviderError(
                    code="CLIENT_INIT_FAILED",
                    message=f"Failed to initialize OpenAI client: {str(e)}",
                )
        return self._client

    def _generate_json(self, prompt: str, system_message: str = "You are the AI intelligence layer of SkillSync. You must respond in valid JSON.") -> Dict[str, Any]:
        """Calls OpenAI chat completion with JSON object response format."""
        client = self._get_client()
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw_text = response.choices[0].message.content or "{}"
            parsed = json.loads(raw_text)
            if not isinstance(parsed, dict):
                raise ValueError("Response is not a valid JSON dictionary.")
            return parsed
        except json.JSONDecodeError as e:
            raise AIProviderError(
                code="MALFORMED_AI_RESPONSE",
                message=f"OpenAI returned invalid JSON: {str(e)}",
            )
        except Exception as e:
            err_msg = str(e)
            if "insufficient_quota" in err_msg.lower() or "credit_balance_exhausted" in err_msg.lower() or "429" in err_msg:
                code = "AI_QUOTA_EXHAUSTED"
            elif "auth" in err_msg.lower() or "key" in err_msg.lower() or "401" in err_msg or "403" in err_msg:
                code = "AI_AUTH_FAILED"
            else:
                code = "AI_PROVIDER_ERROR"
            raise AIProviderError(code=code, message=f"OpenAI generation failed: {err_msg}")

    def analyze_skills(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""
A student provided the following skills or technical background:
{user_input}

Context: {json.dumps(context or {})}

Extract and evaluate their technical profile.
Return ONLY valid JSON with this exact schema:
{{
    "extracted_skills": ["Skill1", "Skill2"],
    "domain_focus": "Primary technical domain",
    "suggested_role": "Target career role matching these skills",
    "suggested_competency_level": "Beginner | Intermediate | Advanced",
    "strengths": ["Demonstrated strength 1", "Demonstrated strength 2"],
    "missing_skills": ["Skill gap 1", "Skill gap 2"],
    "recommended_skills": ["Recommended next skill 1", "Recommended next skill 2"],
    "summary": "Brief summary of candidate capability"
}}
"""
        return self._generate_json(prompt)

    def analyze_resume(self, resume_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""
Extract structured competency evidence and qualifications from this candidate's resume.

Resume Text:
{resume_text[:6000]}

Context: {json.dumps(context or {})}

Return ONLY valid JSON with this exact schema:
{{
    "candidate_name": "Full name if found, else null",
    "current_title": "Current or most recent job title",
    "skills": ["Skill1", "Skill2"],
    "experience_years_estimate": 2,
    "experience_summary": "Brief summary of work history",
    "strengths": ["Key strength 1", "Key strength 2"],
    "projects": ["Project title or highlight 1", "Project title or highlight 2"],
    "education": ["Degree or education detail"]
}}
"""
        return self._generate_json(prompt)

    def analyze_job_description(self, job_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""
Analyze this job description and extract target competencies.

Job Description:
{job_text[:6000]}

Context: {json.dumps(context or {})}

Return ONLY valid JSON with this exact schema:
{{
    "role": "Standardized job title",
    "company": "Company name if mentioned, else null",
    "required_skills": ["Mandatory skill 1", "Mandatory skill 2"],
    "preferred_skills": ["Bonus/preferred skill 1", "Bonus/preferred skill 2"],
    "competency_expectations": [
        {{"skill": "SkillName", "level": "Beginner|Intermediate|Advanced", "criticality": "HIGH|MEDIUM|LOW"}}
    ],
    "responsibilities": ["Core responsibility 1", "Core responsibility 2"]
}}
"""
        return self._generate_json(prompt)

    def generate_interview_questions(self, role: str, skills: List[str], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        prompt = f"""
Generate 3 realistic, targeted technical interview questions for the role: '{role}' covering skills: {skills}.

Return ONLY valid JSON:
{{
    "questions": [
        {{
            "id": 1,
            "skill": "Target Skill",
            "question": "Clear technical question",
            "difficulty": "Beginner|Intermediate|Advanced",
            "evaluation_criteria": ["Criteria 1", "Criteria 2"]
        }}
    ]
}}
"""
        res = self._generate_json(prompt)
        return res.get("questions", [])

    def evaluate_interview_response(self, question: str, response_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""
Evaluate this student's response to the interview question.

Question: {question}
Student Response: {response_text}

Return ONLY valid JSON:
{{
    "score": 85,
    "confidence": 0.8,
    "feedback": "constructive feedback",
    "strengths": ["strength 1"],
    "improvement_areas": ["area 1"]
}}
"""
        return self._generate_json(prompt)

    def analyze_project(self, project_description: str, repo_url: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""
Analyze this technical project for evidence of skill application.

Project Description: {project_description}
Repository URL: {repo_url or "None"}

Return ONLY valid JSON:
{{
    "applied_skills": ["Skill1", "Skill2"],
    "project_complexity": "LOW|MEDIUM|HIGH",
    "architecture_highlights": ["Highlight 1"],
    "code_quality_indicators": ["Indicator 1"]
}}
"""
        return self._generate_json(prompt)
