"""
SkillSync Application Entry Point & Route Registration.

Clean MVC layer:
- No provider SDK imports or API keys inside app.py
- Delegates AI tasks to AIService
- Delegates competency & scoring to CompetencyEngine
- Delegates learning pathways to LearningService
"""

import io
from flask import Flask, render_template, request, jsonify

from backend.config import Config
from backend.services.ai_service import get_ai_service
from backend.services.learning_service import get_learning_service
from backend.competency_engine import get_competency_engine
from backend.providers.base import AIProviderError


app = Flask(
    __name__,
    template_folder=Config.BASE_DIR / "frontend" / "templates",
    static_folder=Config.BASE_DIR / "frontend" / "static",
)
app.config["SECRET_KEY"] = Config.SECRET_KEY


# =====================================
# HOME PAGE
# =====================================

@app.route("/")
def home():
    """Renders the SkillSync main interface."""
    return render_template("index.html")


# =====================================
# SYSTEM HEALTH API
# =====================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Returns application, provider, and taxonomy health status."""
    ai_service = get_ai_service()
    competency_engine = get_competency_engine()

    return jsonify({
        "status": "healthy",
        "service": "SkillSync",
        "ai_provider": ai_service.get_status(),
        "taxonomy_skills_count": len(competency_engine.taxonomy.get_all_canonical_names()),
    }), 200


# =====================================
# SKILL ANALYSIS API
# =====================================

@app.route("/analyze-skills", methods=["POST"])
def analyze_skills_route():
    """
    Skill Analysis Route.
    Flow:
      Request -> AIService (extraction) -> CompetencyEngine (deterministic scoring)
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "No JSON data received.",
                },
                "message": "No data received."
            }), 400

        skills_text = data.get("skills", "").strip()
        if not skills_text:
            return jsonify({
                "success": False,
                "error": {
                    "code": "EMPTY_SKILLS",
                    "message": "Please enter at least one skill.",
                },
                "message": "Please enter at least one skill."
            }), 400

        ai_service = get_ai_service()
        competency_engine = get_competency_engine()

        ai_extracted = None
        # Attempt AI extraction if provider is available
        try:
            ai_extracted = ai_service.analyze_skills(skills_text)
        except AIProviderError as e:
            # Per Section 18: Skill normalization + rule categorization works deterministically
            # even when AI is offline, but we log the provider note.
            print(f"Notice: AI skills extraction skipped ({e.code}): {e.message}")
            ai_extracted = None
        except Exception as e:
            print(f"Notice: AI skills extraction fallback: {e}")
            ai_extracted = None

        # Always execute deterministic competency engine for scoring & gaps
        result = competency_engine.evaluate_skills_profile(skills_text, ai_extracted=ai_extracted)
        return jsonify(result), 200

    except Exception as error:
        print("SKILL ANALYSIS ROUTE ERROR:", error)
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while analyzing skills.",
            },
            "message": "Something went wrong while analyzing skills."
        }), 500


# =====================================
# RESUME ANALYSIS API
# =====================================

@app.route("/analyze-resume", methods=["POST"])
def analyze_resume_route():
    """
    Resume & Job Description Analysis Route.
    Flow:
    Upload -> Text Extraction -> AIService -> CompetencyEngine (evidence scoring)
    """
    try:
        resume_file = request.files.get("resume")
        job_description = request.form.get("job_description", "").strip()

        if not resume_file or not resume_file.filename:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_RESUME_FILE",
                    "message": "Please upload a resume file (.txt or .pdf).",
                },
                "message": "Please upload your resume."
            }), 400

        if not job_description:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_JOB_DESCRIPTION",
                    "message": "Please provide a job description.",
                },
                "message": "Please provide a job description."
            }), 400

        # Extract text from uploaded resume
        filename = resume_file.filename.lower()
        resume_text = ""

        if filename.endswith(".pdf"):
            try:
                from pypdf import PdfReader
                pdf_reader = PdfReader(io.BytesIO(resume_file.read()))
                pages = [page.extract_text() or "" for page in pdf_reader.pages]
                resume_text = "\n".join(pages).strip()
            except Exception as pdf_err:
                print("PDF extraction failed, attempting raw text decode:", pdf_err)
                resume_file.seek(0)
                resume_text = resume_file.read().decode("utf-8", errors="ignore").strip()
        elif filename.endswith((".txt", ".md")):
            resume_text = resume_file.read().decode("utf-8", errors="ignore").strip()
        else:
            return jsonify({
                "success": False,
                "error": {
                    "code": "UNSUPPORTED_FILE_TYPE",
                    "message": "Unsupported file format. Please upload a .txt or .pdf resume.",
                },
                "message": "Unsupported file format. Please upload a .txt or .pdf resume."
            }), 400

        if not resume_text:
            return jsonify({
                "success": False,
                "error": {
                    "code": "EMPTY_RESUME_TEXT",
                    "message": "Could not extract text from the resume file. Please ensure it is not empty or password protected.",
                },
                "message": "Could not extract text from the uploaded resume."
            }), 400

        ai_service = get_ai_service()
        competency_engine = get_competency_engine()

        # Step 1: Check AI provider availability
        available, reason = ai_service.provider.is_available()
        if not available:
            # Per Section 18: Do NOT fake AI resume reasoning if AI provider is unavailable.
            # Return clear error.
            return jsonify({
                "success": False,
                "error": {
                    "code": "AI_PROVIDER_UNAVAILABLE",
                    "message": f"AI resume reasoning is unavailable: {reason}",
                },
                "message": f"AI analysis unavailable ({reason}). Please configure your API key."
            }), 503

        # Step 2: AI extraction for resume and job description
        try:
            resume_data = ai_service.analyze_resume(resume_text)
            job_data = ai_service.analyze_job_description(job_description)
        except AIProviderError as e:
            return jsonify({
                "success": False,
                "error": {
                    "code": e.code,
                    "message": e.message,
                },
                "message": f"AI analysis failed: {e.message}"
            }), 502

        # Step 3: Deterministic competency & match evaluation
        result = competency_engine.evaluate_resume_and_job(
            resume_data=resume_data,
            job_data=job_data,
            raw_resume_text=resume_text,
            raw_job_text=job_description,
        )

        return jsonify(result), 200

    except Exception as error:
        print("RESUME ANALYSIS ROUTE ERROR:", error)
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while analyzing the resume.",
            },
            "message": "Something went wrong while analyzing your resume."
        }), 500


# =====================================
# COURSES / LEARNING API
# =====================================

@app.route("/courses", methods=["GET"])
def courses_route():
    """
    Learning Resources Route (Restored & Enhanced).
    Returns verified, curated learning resources mapped to competency gaps.
    """
    try:
        learning_service = get_learning_service()
        target_skill = request.args.get("skill")
        gap_skills = request.args.getlist("gaps")

        if gap_skills:
            courses = learning_service.recommend_courses_for_gaps(gap_skills)
        elif target_skill:
            courses = learning_service.get_courses_by_skill(target_skill)
        else:
            courses = learning_service.get_all_courses()

        return jsonify({
            "success": True,
            "count": len(courses),
            "courses": courses,
        }), 200

    except Exception as error:
        print("COURSES ROUTE ERROR:", error)
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Failed to load learning resources.",
            }
        }), 500


# =====================================
# AI MOCK INTERVIEW API
# =====================================

@app.route("/api/mock-interview/start", methods=["POST"])
def start_mock_interview():
    """
    Starts an AI mock interview.

    Generates the initial interview questions based on:
    - Target role
    - Candidate skills
    """

    try:
        data = request.get_json(silent=True) or {}

        role = str(data.get("role", "Software Engineer")).strip()
        skills = data.get("skills", [])

        if not isinstance(skills, list):
            skills = []

        skills = [
            str(skill).strip()
            for skill in skills
            if str(skill).strip()
        ]

        if not skills:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_SKILLS",
                    "message": "At least one skill is required to start the interview."
                },
                "message": "Please provide at least one skill."
            }), 400

        ai_service = get_ai_service()

        # Verify that the configured AI provider is available.
        available, reason = ai_service.provider.is_available()

        if not available:
            return jsonify({
                "success": False,
                "error": {
                    "code": "AI_PROVIDER_UNAVAILABLE",
                    "message": reason
                },
                "message": f"AI interview unavailable: {reason}"
            }), 503

        questions = ai_service.provider.generate_interview_questions(
            role=role,
            skills=skills,
            context={
                "interview_type": "technical",
                "adaptive": True
            }
        )

        if not questions:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NO_INTERVIEW_QUESTIONS",
                    "message": "The AI provider did not generate interview questions."
                },
                "message": "Could not generate interview questions."
            }), 502

        return jsonify({
            "success": True,
            "role": role,
            "skills": skills,
            "total_questions": len(questions),
            "questions": questions
        }), 200

    except AIProviderError as error:
        return jsonify({
            "success": False,
            "error": error.to_dict(),
            "message": f"Interview generation failed: {error.message}"
        }), 502

    except Exception as error:
        print("MOCK INTERVIEW START ERROR:", error)

        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while starting the interview."
            },
            "message": "Something went wrong while starting the interview."
        }), 500


@app.route("/api/mock-interview/evaluate", methods=["POST"])
def evaluate_mock_interview_response():
    """
    Evaluates a student's spoken interview response.

    Speech-to-text happens in the browser.
    The resulting transcript is sent here for Gemini evaluation.
    """

    try:
        data = request.get_json(silent=True) or {}

        question = str(data.get("question", "")).strip()
        response_text = str(data.get("response", "")).strip()

        if not question:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_QUESTION",
                    "message": "Interview question is required."
                },
                "message": "Interview question is missing."
            }), 400

        if not response_text:
            return jsonify({
                "success": False,
                "error": {
                    "code": "EMPTY_RESPONSE",
                    "message": "Candidate response cannot be empty."
                },
                "message": "Please provide an answer."
            }), 400

        ai_service = get_ai_service()

        available, reason = ai_service.provider.is_available()

        if not available:
            return jsonify({
                "success": False,
                "error": {
                    "code": "AI_PROVIDER_UNAVAILABLE",
                    "message": reason
                },
                "message": f"AI interview unavailable: {reason}"
            }), 503

        evaluation = ai_service.provider.evaluate_interview_response(
            question=question,
            response_text=response_text,
            context={
                "interview_type": "technical",
                "response_mode": "voice_transcript"
            }
        )

        return jsonify({
            "success": True,
            "evaluation": evaluation
        }), 200

    except AIProviderError as error:
        return jsonify({
            "success": False,
            "error": error.to_dict(),
            "message": f"Interview evaluation failed: {error.message}"
        }), 502

    except Exception as error:
        print("MOCK INTERVIEW EVALUATION ERROR:", error)

        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while evaluating the interview response."
            },
            "message": "Something went wrong while evaluating your answer."
        }), 500


@app.route("/api/mock-interview/follow-up", methods=["POST"])
def generate_mock_interview_follow_up():
    """
    Generates the next adaptive interview question.

    Gemini uses:
    - Previous question
    - Candidate's answer
    - Previous evaluation
    - Target role
    """

    try:
        data = request.get_json(silent=True) or {}

        role = str(data.get("role", "Software Engineer")).strip()
        previous_question = str(data.get("previous_question", "")).strip()
        response_text = str(data.get("response", "")).strip()
        evaluation = data.get("evaluation", {})

        if not previous_question:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_PREVIOUS_QUESTION",
                    "message": "Previous interview question is required."
                },
                "message": "Previous question is missing."
            }), 400

        if not response_text:
            return jsonify({
                "success": False,
                "error": {
                    "code": "EMPTY_RESPONSE",
                    "message": "Candidate response cannot be empty."
                },
                "message": "Candidate response is missing."
            }), 400

        if not isinstance(evaluation, dict):
            evaluation = {}

        ai_service = get_ai_service()

        available, reason = ai_service.provider.is_available()

        if not available:
            return jsonify({
                "success": False,
                "error": {
                    "code": "AI_PROVIDER_UNAVAILABLE",
                    "message": reason
                },
                "message": f"AI interview unavailable: {reason}"
            }), 503

        next_question = ai_service.generate_follow_up_question(
            role=role,
            previous_question=previous_question,
            response_text=response_text,
            evaluation=evaluation,
            context={
                "interview_type": "technical",
                "adaptive": True,
                "response_mode": "voice_transcript"
            }
        )

        return jsonify({
            "success": True,
            "question": next_question
        }), 200

    except AIProviderError as error:
        return jsonify({
            "success": False,
            "error": error.to_dict(),
            "message": f"Follow-up generation failed: {error.message}"
        }), 502

    except Exception as error:
        print("MOCK INTERVIEW FOLLOW-UP ERROR:", error)

        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while generating the next question."
            },
            "message": "Something went wrong while generating the next question."
        }), 500
# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":
    app.run(
        debug=Config.DEBUG,
        port=Config.PORT,
    )