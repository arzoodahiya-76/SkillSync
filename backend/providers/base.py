"""
SkillSync Base AI Provider Interface.

Defines the contract for AI providers (Gemini, OpenAI, etc.).
Enforces provider independence: callers communicate strictly through this interface
and receive normalized structured data.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class AIProviderError(Exception):
    """Standard exception raised when an AI provider fails."""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class AIProvider(ABC):
    """Abstract Base Class for all SkillSync AI Providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the identifier of the provider (e.g. 'gemini', 'openai')."""
        pass

    @abstractmethod
    def is_available(self) -> tuple[bool, str]:
        """
        Checks whether the provider is configured and available.
        Returns: (is_available: bool, reason: str)
        """
        pass

    @abstractmethod
    def analyze_skills(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extracts and analyzes skills from unstructured student input.
        Returns structured JSON dict.
        """
        pass

    @abstractmethod
    def analyze_resume(self, resume_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extracts candidate skills, experiences, and qualifications from resume text.
        Returns structured JSON dict.
        """
        pass

    @abstractmethod
    def analyze_job_description(self, job_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extracts role, required skills, preferred skills, responsibilities, and criticality.
        Returns structured JSON dict.
        """
        pass

    @abstractmethod
    def generate_interview_questions(self, role: str, skills: List[str], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generates targeted interview questions based on role and skills.
        Returns list of structured question dicts.
        """
        pass

    @abstractmethod
    def evaluate_interview_response(self, question: str, response_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluates a candidate's answer to an interview question.
        Returns structured JSON evaluation dict.
        """
        pass

    @abstractmethod
    def analyze_project(self, project_description: str, repo_url: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes a technical project description or repository for skill evidence.
        Returns structured JSON evaluation dict.
        """
        pass
