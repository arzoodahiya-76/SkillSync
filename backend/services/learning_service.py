"""
SkillSync Learning Resource Service.

Provides verified, curated learning resources from trusted global providers
(Coursera, edX, Microsoft Learn, Google Cloud Skills Boost, AWS Training, freeCodeCamp).
Matches learning pathways directly to identified competency gaps.
SkillSync is NOT a course marketplace; it recommends targeted interventions.
"""

from typing import List, Dict, Optional, Any
from backend.taxonomy import get_taxonomy


# Curated, verified course metadata mapped to competencies
CURATED_LEARNING_CATALOGUE: List[Dict[str, Any]] = [
    {
        "id": "py-01",
        "name": "Python for Everybody Specialization",
        "provider": "Coursera (University of Michigan)",
        "level": "Beginner",
        "duration": "8 Months (3 hrs/week)",
        "certificate": "Verified Certificate Available",
        "url": "https://www.coursera.org/specializations/python",
        "skills_covered": ["Python", "Data Structures", "SQL"],
        "description": "Fundamental programming and data manipulation using Python.",
    },
    {
        "id": "dsa-01",
        "name": "Data Structures and Algorithms Specialization",
        "provider": "Coursera (UC San Diego)",
        "level": "Intermediate",
        "duration": "6 Months (4 hrs/week)",
        "certificate": "Verified Certificate Available",
        "url": "https://www.coursera.org/specializations/data-structures-algorithms",
        "skills_covered": ["Data Structures", "Algorithms", "C++", "Java", "Python"],
        "description": "Master algorithmic techniques, graph algorithms, and asymptotic analysis.",
    },
    {
        "id": "web-01",
        "name": "Full Stack Web Development with React Specialization",
        "provider": "Coursera (HKUST)",
        "level": "Intermediate",
        "duration": "4 Months (5 hrs/week)",
        "certificate": "Verified Certificate Available",
        "url": "https://www.coursera.org/specializations/full-stack-react",
        "skills_covered": ["React", "JavaScript", "HTML", "CSS", "Node.js"],
        "description": "Front-end and multiplatform mobile development with React and JavaScript.",
    },
    {
        "id": "flask-01",
        "name": "Building RESTful APIs with Flask",
        "provider": "freeCodeCamp / Official Docs",
        "level": "Intermediate",
        "duration": "4 Weeks",
        "certificate": "Open Source Curriculum",
        "url": "https://flask.palletsprojects.com/",
        "skills_covered": ["Flask", "Python", "REST API", "SQL"],
        "description": "Design, develop, and secure production-grade REST APIs in Python using Flask.",
    },
    {
        "id": "ml-01",
        "name": "Machine Learning Specialization",
        "provider": "Coursera (DeepLearning.AI & Stanford)",
        "level": "Advanced",
        "duration": "3 Months (7 hrs/week)",
        "certificate": "Verified Certificate Available",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "skills_covered": ["Machine Learning", "Python", "NumPy", "Pandas", "Scikit-Learn"],
        "description": "Foundational and modern machine learning concepts taught by Andrew Ng.",
    },
    {
        "id": "gcp-01",
        "name": "Google Cloud Computing Foundations",
        "provider": "Google Cloud Skills Boost",
        "level": "Beginner to Intermediate",
        "duration": "4 Weeks",
        "certificate": "Google Cloud Digital Badge",
        "url": "https://www.cloudskillsboost.google/",
        "skills_covered": ["Cloud Computing", "GCP", "Linux", "DevOps"],
        "description": "Learn cloud infrastructure, networking, and data processing on Google Cloud.",
    },
    {
        "id": "ms-01",
        "name": "Microsoft Azure Fundamentals (AZ-900)",
        "provider": "Microsoft Learn",
        "level": "Beginner",
        "duration": "3 Weeks",
        "certificate": "Microsoft Proctored Exam Preparation",
        "url": "https://learn.microsoft.com/en-us/training/courses/az-900t00",
        "skills_covered": ["Cloud Computing", "AWS", "Azure", "Security"],
        "description": "Master foundational cloud services, security, privacy, and compliance on Azure.",
    },
    {
        "id": "docker-01",
        "name": "Docker and Kubernetes: The Complete Guide",
        "provider": "edX / Linux Foundation",
        "level": "Intermediate",
        "duration": "6 Weeks",
        "certificate": "Verified Certificate Available",
        "url": "https://www.edx.org/learn/docker",
        "skills_covered": ["Docker", "Kubernetes", "DevOps", "Git"],
        "description": "Container creation, orchestration, deployment pipelines, and microservices.",
    },
    {
        "id": "sql-01",
        "name": "Databases and SQL for Data Science",
        "provider": "IBM (edX / Coursera)",
        "level": "Beginner",
        "duration": "5 Weeks (3 hrs/week)",
        "certificate": "IBM Professional Badge",
        "url": "https://www.coursera.org/learn/sql-data-science",
        "skills_covered": ["SQL", "Relational Databases", "Data Analysis"],
        "description": "Write advanced SQL queries, aggregate data, and integrate databases with Python.",
    },
]


class LearningService:
    """Service to recommend learning pathways matching verified competency gaps."""

    def __init__(self, catalogue: Optional[List[Dict[str, Any]]] = None):
        self.catalogue = catalogue or CURATED_LEARNING_CATALOGUE
        self.taxonomy = get_taxonomy()

    def get_all_courses(self) -> List[Dict[str, Any]]:
        """Returns all curated courses."""
        return self.catalogue

    def get_courses_by_skill(self, target_skill: str) -> List[Dict[str, Any]]:
        """Filters courses by target skill or its canonical normalized name."""
        canonical = self.taxonomy.normalize(target_skill) or target_skill.strip().title()
        canonical_lower = canonical.lower()

        matched = []
        for course in self.catalogue:
            skills = [s.lower() for s in course.get("skills_covered", [])]
            if canonical_lower in skills or any(canonical_lower in s for s in skills):
                matched.append(course)
        return matched

    def recommend_courses_for_gaps(self, gap_skills: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Matches identified skill gaps against learning resources.
        Ranks courses by the number of gap skills they resolve.
        """
        normalized_gaps = set()
        for g in gap_skills:
            canonical = self.taxonomy.normalize(g) or g.strip().title()
            normalized_gaps.add(canonical.lower())

        scored_courses = []
        for course in self.catalogue:
            course_skills = {s.lower() for s in course.get("skills_covered", [])}
            overlap = normalized_gaps.intersection(course_skills)
            if overlap:
                scored_courses.append({
                    "course": course,
                    "overlap_count": len(overlap),
                    "covered_gaps": [s.title() for s in overlap],
                })

        # Sort descending by overlap count
        scored_courses.sort(key=lambda x: x["overlap_count"], reverse=True)

        recommendations = []
        for item in scored_courses[:limit]:
            course_copy = dict(item["course"])
            course_copy["resolved_gaps"] = item["covered_gaps"]
            recommendations.append(course_copy)

        return recommendations


_learning_service_instance: Optional[LearningService] = None


def get_learning_service() -> LearningService:
    global _learning_service_instance
    if _learning_service_instance is None:
        _learning_service_instance = LearningService()
    return _learning_service_instance
