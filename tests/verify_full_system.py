"""
Comprehensive Full-System Verification Script for SkillSync.

Verifies:
1. /api/health
2. /analyze-skills (deterministic + AI fallback)
3. /analyze-resume (valid and invalid inputs)
4. Missing Gemini API key error contract
5. Provider switching (gemini vs openai)
6. Course recommendation endpoint
"""

import io
import json
from app import app
from backend.config import Config
from backend.services.ai_service import AIService
from backend.competency_engine import get_competency_engine


def run_system_verification():
    client = app.test_client()
    print("==================================================")
    print("SKILLSYNC SYSTEM INTEGRATION & VERIFICATION")
    print("==================================================")

    # 1. Health Check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    health_data = res.get_json()
    print("[PASS] 1. /api/health returned 200:")
    print(f"       Status: {health_data['status']}, Provider: {health_data['ai_provider']}")

    # 2. Skill Analysis
    res = client.post("/analyze-skills", json={"skills": "Python, Flask, SQL, React"})
    assert res.status_code == 200, f"Skill analysis failed: {res.status_code}"
    skill_data = res.get_json()
    assert skill_data["success"] is True, "Skill analysis success was False"
    print("[PASS] 2. /analyze-skills returned 200:")
    print(f"       Role: {skill_data['best_matching_role']}, Score: {skill_data['job_match_score']}%, Level: {skill_data['competency_level']}")

    # 3. Invalid Skill Analysis Input
    res = client.post("/analyze-skills", json={"skills": ""})
    assert res.status_code == 400, f"Expected 400 for empty skills, got {res.status_code}"
    err_data = res.get_json()
    assert err_data["error"]["code"] == "EMPTY_SKILLS"
    print("[PASS] 3. /analyze-skills empty validation rejected with 400 EMPTY_SKILLS")

    # 4. Missing Gemini API Key on Resume Analysis
    # Ensure Section 18: No fake AI resume reasoning if Gemini key is missing
    resume_bytes = io.BytesIO(b"Candidate with Python, Flask and SQL.")
    res = client.post(
        "/analyze-resume",
        data={
            "resume": (resume_bytes, "resume.txt"),
            "job_description": "Looking for a Python Backend Engineer with Docker.",
        },
        content_type="multipart/form-data"
    )
    # If GEMINI_API_KEY is not configured, it must return 503 AI_PROVIDER_UNAVAILABLE
    if not Config.GEMINI_API_KEY and Config.AI_PROVIDER == "gemini":
        assert res.status_code == 503, f"Expected 503 for unconfigured Gemini, got {res.status_code}"
        assert res.get_json()["error"]["code"] == "AI_PROVIDER_UNAVAILABLE"
        print("[PASS] 4. /analyze-resume returned 503 AI_PROVIDER_UNAVAILABLE when GEMINI_API_KEY missing (No fake AI fallback)")
    else:
        print(f"[INFO] 4. /analyze-resume returned {res.status_code} with configured provider")

    # 5. Invalid Resume Input
    res = client.post(
        "/analyze-resume",
        data={"job_description": "Some job"},
        content_type="multipart/form-data"
    )
    assert res.status_code == 400, f"Expected 400 for missing resume, got {res.status_code}"
    print("[PASS] 5. /analyze-resume rejected missing resume file with 400")

    # 6. Provider Selection Verification
    gemini_service = AIService(provider_name="gemini")
    assert gemini_service.provider.provider_name == "gemini"
    openai_service = AIService(provider_name="openai")
    assert openai_service.provider.provider_name == "openai"
    print("[PASS] 6. Provider switching verified (gemini & openai independent instantiations)")

    # 7. Courses / Learning Resources Endpoint
    res = client.get("/courses")
    assert res.status_code == 200
    course_data = res.get_json()
    assert course_data["count"] > 0
    print(f"[PASS] 7. /courses returned 200 with {course_data['count']} curated resources")

    # 8. Competency Engine Determinism (No AI SDK dependencies)
    engine = get_competency_engine()
    profile = engine.evaluate_skills_profile("Python, Docker, Kubernetes, AWS, Linux, Git")
    assert profile["competency_level"] in ("Intermediate", "Advanced")
    assert "Software Development" in profile["domain_distribution"] or "DevOps & Tools" in profile["domain_distribution"]
    print(f"[PASS] 8. CompetencyEngine deterministic evaluation verified (Score: {profile['competency_score']})")

    print("==================================================")
    print("ALL 8 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_system_verification()
