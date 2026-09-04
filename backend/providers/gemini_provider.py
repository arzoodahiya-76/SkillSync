"""
SkillSync Google Gemini AI Provider (Primary).

Implements AIProvider using Google's current official `google-genai` SDK.
Returns validated structured JSON output.
Never exposes API keys to clients.
"""

import json
from typing import Dict, List, Optional, Any

from backend.config import Config
from backend.providers.base import AIProvider, AIProviderError


class GeminiProvider(AIProvider):
    """Primary AI provider using Google's official google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else Config.GEMINI_API_KEY
        self.model = model or Config.GEMINI_MODEL
        self._client = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    def is_available(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "GEMINI_API_KEY is not configured in environment."
        return True, "Ready"

    def _get_client(self):
        """Initializes the official google-genai client."""
        if self._client is None:
            available, reason = self.is_available()
            if not available:
                raise AIProviderError(
                    code="GEMINI_NOT_CONFIGURED",
                    message=f"Gemini provider is not configured: {reason}",
                )
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                raise AIProviderError(
                    code="SDK_NOT_INSTALLED",
                    message="The google-genai SDK is not installed in the Python environment.",
                )
            except Exception as e:
                raise AIProviderError(
                    code="CLIENT_INIT_FAILED",
                    message=f"Failed to initialize Gemini client: {str(e)}",
                )
        return self._client

    def _generate_json(self, prompt: str) -> Dict[str, Any]:
        """Calls Gemini with enforced JSON response MIME type and parses the result."""
        client = self._get_client()
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            )
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            raw_text = response.text or "{}"
            parsed = json.loads(raw_text)
            if not isinstance(parsed, dict):
                raise ValueError("Response is not a valid JSON dictionary.")
            return parsed
        except json.JSONDecodeError as e:
            raise AIProviderError(
                code="MALFORMED_AI_RESPONSE",
                message=f"Gemini returned invalid JSON: {str(e)}",
            )
        except Exception as e:
            err_msg = str(e)
            if "quota" in err_msg.lower() or "429" in err_msg:
                code = "AI_QUOTA_EXHAUSTED"
            elif "auth" in err_msg.lower() or "key" in err_msg.lower() or "403" in err_msg or "401" in err_msg:
                code = "AI_AUTH_FAILED"
            else:
                code = "AI_PROVIDER_ERROR"
            raise AIProviderError(code=code, message=f"Gemini generation failed: {err_msg}")

    def analyze_skills(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""
You are the AI extraction layer of SkillSync, an intelligent competency and career guidance platform.
A student provided the following skills or background:
{user_input}

Context (if available): {json.dumps(context or {})}

Extract and evaluate their technical profile.
Return ONLY valid JSON with this exact schema:
{{
    "extracted_skills": ["Skill1", "Skill2"],
    "domain_focus": "Primary technical domain (e.g. Web Development, Data Science)",
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
You are an expert AI resume reviewer at SkillSync.
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
You are an expert AI talent acquisition analyst at SkillSync.
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
You are an AI technical interviewer for SkillSync.
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
You are an AI assessment evaluator for SkillSync.
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
    
    def generate_follow_up_question(
        self,
        role: str,
        previous_question: str,
        response_text: str,
        evaluation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates an adaptive follow-up interview question based on
        the candidate's previous answer and evaluation.
        """

        prompt = f"""
You are conducting an adaptive AI interview for SkillSync.

Role:
{role}

Previous Interview Question:
{previous_question}

Candidate's Verbal Response:
{response_text}

Evaluation of Previous Response:
{json.dumps(evaluation)}

Additional Context:
{json.dumps(context or {})}

Your task is to generate ONE realistic follow-up interview question.

The question should adapt to the candidate's previous answer.

Rules:
1. If the answer was strong, increase depth or difficulty.
2. If the answer was partially correct, ask a clarifying or deeper question.
3. If the answer was weak, ask a simpler foundational question that tests the same competency.
4. Do not repeat the previous question.
5. Keep the question suitable for a spoken interview.
6. Do not ask multiple questions at once.
7. Focus on technical reasoning and demonstrated understanding.
8. Do not make unsupported assumptions about the candidate.

Return ONLY valid JSON using this exact schema:

{{
    "skill": "Target Skill",
    "question": "One clear interview question",
    "difficulty": "Beginner|Intermediate|Advanced",
    "reason": "Brief explanation of why this question was selected",
    "evaluation_criteria": [
        "Criterion 1",
        "Criterion 2",
        "Criterion 3"
    ]
}}
"""

        result = self._generate_json(prompt)

        return {
            "skill": str(result.get("skill", "General Technical Skills")),
            "question": str(result.get("question", "")),
            "difficulty": str(result.get("difficulty", "Intermediate")),
            "reason": str(result.get("reason", "")),
            "evaluation_criteria": [
                str(item)
                for item in result.get("evaluation_criteria", [])
                if isinstance(item, str)
            ],
        }

    def analyze_project(self, project_description: str, repo_url: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""
You are an AI technical project reviewer for SkillSync.
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
