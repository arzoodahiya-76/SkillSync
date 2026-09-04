"""
SkillSync Taxonomy & Skill Data Management.

Restores and extends data/skills.csv loading.
Supports rich taxonomy structure:
  - skill name (canonical)
  - domain
  - category
  - aliases (synonyms, acronyms)
  - default proficiency metadata (levels: Beginner, Intermediate, Advanced)
"""

import csv
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

from backend.config import Config


@dataclass
class SkillMetadata:
    """Represents a standardized skill item within the SkillSync taxonomy."""
    name: str
    domain: str
    category: str
    aliases: List[str] = field(default_factory=list)
    default_proficiency_benchmark: str = "Intermediate"
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "domain": self.domain,
            "category": self.category,
            "aliases": self.aliases,
            "default_proficiency_benchmark": self.default_proficiency_benchmark,
            "description": self.description,
        }


# Taxonomy domain definitions and curated metadata mappings
TAXONOMY_ENRICHMENT: Dict[str, dict] = {
    "python": {
        "domain": "Software Development",
        "category": "Programming Languages",
        "aliases": ["py", "python3"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "java": {
        "domain": "Software Development",
        "category": "Programming Languages",
        "aliases": ["jdk", "core java"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "c++": {
        "domain": "Systems & Embedded",
        "category": "Programming Languages",
        "aliases": ["cpp", "cplusplus"],
        "default_proficiency_benchmark": "Advanced",
    },
    "javascript": {
        "domain": "Web Development",
        "category": "Frontend Technologies",
        "aliases": ["js", "es6", "vanilla js"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "html": {
        "domain": "Web Development",
        "category": "Frontend Technologies",
        "aliases": ["html5"],
        "default_proficiency_benchmark": "Beginner",
    },
    "css": {
        "domain": "Web Development",
        "category": "Frontend Technologies",
        "aliases": ["css3"],
        "default_proficiency_benchmark": "Beginner",
    },
    "react": {
        "domain": "Web Development",
        "category": "Frontend Frameworks",
        "aliases": ["react.js", "reactjs"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "flask": {
        "domain": "Web Development",
        "category": "Backend Frameworks",
        "aliases": ["flask framework"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "django": {
        "domain": "Web Development",
        "category": "Backend Frameworks",
        "aliases": ["django framework"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "sql": {
        "domain": "Data Management",
        "category": "Databases & Query Languages",
        "aliases": ["relational databases", "mysql", "postgresql", "sqlite"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "mongodb": {
        "domain": "Data Management",
        "category": "NoSQL Databases",
        "aliases": ["mongo", "nosql"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "git": {
        "domain": "DevOps & Tools",
        "category": "Version Control",
        "aliases": ["git vcs", "version control"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "github": {
        "domain": "DevOps & Tools",
        "category": "Collaboration Platforms",
        "aliases": ["github actions"],
        "default_proficiency_benchmark": "Beginner",
    },
    "data structures": {
        "domain": "Computer Science",
        "category": "Core Fundamentals",
        "aliases": ["dsa", "data structures and algorithms"],
        "default_proficiency_benchmark": "Advanced",
    },
    "machine learning": {
        "domain": "Artificial Intelligence",
        "category": "Predictive Modeling",
        "aliases": ["ml", "applied machine learning"],
        "default_proficiency_benchmark": "Advanced",
    },
    "artificial intelligence": {
        "domain": "Artificial Intelligence",
        "category": "AI Principles",
        "aliases": ["ai", "genai", "deep learning"],
        "default_proficiency_benchmark": "Advanced",
    },
    "numpy": {
        "domain": "Data Science",
        "category": "Numerical Computing",
        "aliases": ["numpy library"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "pandas": {
        "domain": "Data Science",
        "category": "Data Analysis",
        "aliases": ["pandas library"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "docker": {
        "domain": "DevOps & Tools",
        "category": "Containerization",
        "aliases": ["containers", "containerization"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "kubernetes": {
        "domain": "DevOps & Tools",
        "category": "Container Orchestration",
        "aliases": ["k8s"],
        "default_proficiency_benchmark": "Advanced",
    },
    "aws": {
        "domain": "Cloud Computing",
        "category": "Cloud Platforms",
        "aliases": ["amazon web services"],
        "default_proficiency_benchmark": "Intermediate",
    },
    "rest api": {
        "domain": "Software Development",
        "category": "API Architecture",
        "aliases": ["restful apis", "rest", "web services"],
        "default_proficiency_benchmark": "Intermediate",
    },
}


CANONICAL_CASING: Dict[str, str] = {
    "javascript": "JavaScript",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "numpy": "NumPy",
    "github": "GitHub",
    "scikit-learn": "Scikit-Learn",
    "c++": "C++",
    "sql": "SQL",
    "html": "HTML",
    "css": "CSS",
    "aws": "AWS",
    "gcp": "GCP",
    "ci/cd": "CI/CD",
    "rest api": "REST API",
}


def _to_canonical_casing(name: str) -> str:
    key = name.lower().strip()
    if key in CANONICAL_CASING:
        return CANONICAL_CASING[key]
    if name.isupper():
        return name
    return name.title()


class SkillTaxonomy:
    """Central repository of standardized skills, domains, and aliases."""

    def __init__(self, csv_path: Optional[Path] = None):
        self.csv_path = csv_path or Config.SKILLS_DATA_PATH
        self.skills_by_name: Dict[str, SkillMetadata] = {}
        self.alias_to_canonical: Dict[str, str] = {}
        self._load_taxonomy()

    def _load_taxonomy(self):
        """Loads canonical skills from skills.csv and enriches with domain metadata."""
        raw_skills = []
        if self.csv_path.exists():
            try:
                with open(self.csv_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        for item in row:
                            cleaned = item.strip()
                            if cleaned:
                                raw_skills.append(cleaned)
            except Exception as e:
                print(f"Warning: Failed reading {self.csv_path}: {e}")

        # If CSV is missing or empty, use fallback canonical keys
        if not raw_skills:
            raw_skills = list(TAXONOMY_ENRICHMENT.keys())

        # Build taxonomy items
        for raw_name in raw_skills:
            key = raw_name.lower().strip()
            enrichment = TAXONOMY_ENRICHMENT.get(key, {})
            canonical_name = _to_canonical_casing(raw_name)

            domain = enrichment.get("domain", "General Technology")
            category = enrichment.get("category", "Technical Skills")
            aliases = enrichment.get("aliases", [])
            benchmark = enrichment.get("default_proficiency_benchmark", "Intermediate")

            metadata = SkillMetadata(
                name=canonical_name,
                domain=domain,
                category=category,
                aliases=aliases,
                default_proficiency_benchmark=benchmark,
            )

            self.skills_by_name[key] = metadata
            self.alias_to_canonical[key] = canonical_name

            # Map all aliases to canonical name
            for alias in aliases:
                self.alias_to_canonical[alias.lower().strip()] = canonical_name

        # Also include any enrichment keys not present in CSV
        for key, enrichment in TAXONOMY_ENRICHMENT.items():
            if key not in self.skills_by_name:
                canonical_name = _to_canonical_casing(key)
                aliases = enrichment.get("aliases", [])
                metadata = SkillMetadata(
                    name=canonical_name,
                    domain=enrichment.get("domain", "General Technology"),
                    category=enrichment.get("category", "Technical Skills"),
                    aliases=aliases,
                    default_proficiency_benchmark=enrichment.get("default_proficiency_benchmark", "Intermediate"),
                )
                self.skills_by_name[key] = metadata
                self.alias_to_canonical[key] = canonical_name
                for alias in aliases:
                    self.alias_to_canonical[alias.lower().strip()] = canonical_name

    def normalize(self, skill_input: str) -> Optional[str]:
        """Maps an input string or alias to a canonical skill name if recognized."""
        key = skill_input.lower().strip()
        return self.alias_to_canonical.get(key)

    def get_metadata(self, skill_name: str) -> Optional[SkillMetadata]:
        """Returns metadata for a given skill name or alias."""
        key = skill_name.lower().strip()
        canonical = self.alias_to_canonical.get(key)
        if canonical:
            return self.skills_by_name.get(canonical.lower())
        return None

    def get_all_canonical_names(self) -> List[str]:
        """Returns all canonical skill names in the taxonomy."""
        return [meta.name for meta in self.skills_by_name.values()]

    def get_all_domains(self) -> Set[str]:
        """Returns all unique domains."""
        return {meta.domain for meta in self.skills_by_name.values()}


# Global singleton instance
_global_taxonomy: Optional[SkillTaxonomy] = None


def get_taxonomy() -> SkillTaxonomy:
    global _global_taxonomy
    if _global_taxonomy is None:
        _global_taxonomy = SkillTaxonomy()
    return _global_taxonomy
