"""
SkillSync Evidence Model.

Defines the multi-modal evidence architecture for skill and competency verification.
Enforces the core principle: A single evidence source (e.g. certificate, resume,
or GitHub profile) never automatically guarantees mastery.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any


class EvidenceType(str, Enum):
    """Supported evidence types for competency verification."""
    SELF_CLAIM = "SELF_CLAIM"
    RESUME = "RESUME"
    THEORY_ASSESSMENT = "THEORY_ASSESSMENT"
    PRACTICAL = "PRACTICAL"
    PROJECT = "PROJECT"
    GITHUB = "GITHUB"
    CREDENTIAL = "CREDENTIAL"
    AI_INTERVIEW = "AI_INTERVIEW"
    HUMAN_INTERVIEW = "HUMAN_INTERVIEW"
    EXPERIENCE_LAB = "EXPERIENCE_LAB"
    REAL_WORLD_FEEDBACK = "REAL_WORLD_FEEDBACK"


class VerificationStatus(str, Enum):
    """Status of evidence verification."""
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


# Evidence type base confidence ceilings and weights
# Single evidence sources cannot alone reach 1.0 (mastery)
EVIDENCE_TYPE_WEIGHTS: Dict[EvidenceType, float] = {
    EvidenceType.SELF_CLAIM: 0.15,
    EvidenceType.RESUME: 0.35,
    EvidenceType.CREDENTIAL: 0.45,
    EvidenceType.GITHUB: 0.60,
    EvidenceType.PROJECT: 0.65,
    EvidenceType.THEORY_ASSESSMENT: 0.70,
    EvidenceType.AI_INTERVIEW: 0.80,
    EvidenceType.PRACTICAL: 0.85,
    EvidenceType.HUMAN_INTERVIEW: 0.90,
    EvidenceType.EXPERIENCE_LAB: 0.95,
    EvidenceType.REAL_WORLD_FEEDBACK: 0.95,
}


@dataclass
class EvidenceRecord:
    """Represents a single piece of evidence supporting a competency."""

    competency: str
    evidence_type: EvidenceType
    score: Optional[float] = None  # 0.0 to 100.0 where applicable
    confidence: float = 0.5        # 0.0 to 1.0
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    source: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    explanation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Normalize evidence_type if passed as string
        if isinstance(self.evidence_type, str):
            self.evidence_type = EvidenceType(self.evidence_type)
        if isinstance(self.verification_status, str):
            self.verification_status = VerificationStatus(self.verification_status)

        # Cap confidence based on evidence ceiling
        max_ceiling = EVIDENCE_TYPE_WEIGHTS.get(self.evidence_type, 0.5)
        if self.verification_status != VerificationStatus.VERIFIED:
            max_ceiling *= 0.8
        self.confidence = min(max(self.confidence, 0.0), max_ceiling)

    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence record to dictionary."""
        return {
            "competency": self.competency,
            "evidence_type": self.evidence_type.value,
            "score": self.score,
            "confidence": round(self.confidence, 2),
            "verification_status": self.verification_status.value,
            "source": self.source,
            "timestamp": self.timestamp,
            "explanation": self.explanation,
            "metadata": self.metadata,
        }
