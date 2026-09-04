from flask import Flask, render_template, request, jsonify
import os

from backend.competency_engine import analyze_skills


# ---------------- PATH CONFIGURATION ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------- FLASK APP ----------------

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- SKILL ANALYSIS ----------------

@app.route("/analyze", methods=["POST"])
def skill_analysis():

    try:

        # Safely receive JSON data
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "No skill data received."
            }), 400


        skills_text = data.get("skills", "")

        if not skills_text.strip():
            return jsonify({
                "error": "Please enter at least one skill."
            }), 400


        # Convert comma-separated skills into a list
        user_skills = [
            skill.strip().lower()
            for skill in skills_text.split(",")
            if skill.strip()
        ]


        # Analyze skills
        result = analyze_skills(user_skills)


        return jsonify(result)


    except Exception as e:

        print("SKILL ANALYSIS ERROR:", str(e))

        return jsonify({
            "error": "Something went wrong while analyzing skills.",
            "details": str(e)
        }), 500


# ---------------- RESUME ANALYSIS ----------------

@app.route("/resume-analyze", methods=["POST"])
def resume_analysis():

    try:

        resume = request.files.get("resume")

        job_description = request.form.get(
            "job_description",
            ""
        ).lower()


        # Check resume
        if not resume or resume.filename == "":
            return jsonify({
                "error": "Please upload your resume."
            }), 400


        # Read uploaded file
        try:

            resume_text = resume.read().decode(
                "utf-8",
                errors="ignore"
            ).lower()

        except Exception:

            return jsonify({
                "error": "Unable to read this resume file. Please upload a TXT file."
            }), 400


        # Skills database
        important_skills = [

            "python",
            "java",
            "javascript",
            "html",
            "css",

            "react",
            "flask",
            "django",

            "sql",
            "mongodb",

            "git",
            "github",

            "machine learning",

            "data structures",
            "algorithms",

            "numpy",
            "pandas",

            "c++",
            "c",

            "node.js",
            "express",

            "mysql",

            "data analysis"

        ]


        # ---------------- RESUME SKILLS ----------------

        resume_skills = []

        for skill in important_skills:

            if skill in resume_text:

                resume_skills.append(skill)


        # ---------------- JOB SKILLS ----------------

        job_skills = []

        for skill in important_skills:

            if skill in job_description:

                job_skills.append(skill)


        # ---------------- MATCHED SKILLS ----------------

        matched_skills = []

        for skill in job_skills:

            if skill in resume_skills:

                matched_skills.append(skill)


        # ---------------- MISSING SKILLS ----------------

        missing_skills = []

        for skill in job_skills:

            if skill not in resume_skills:

                missing_skills.append(skill)


        # ---------------- MATCH SCORE ----------------

        if len(job_skills) > 0:

            match_score = round(

                len(matched_skills)
                / len(job_skills)
                * 100

            )

        else:

            # If no job description is provided
            match_score = 0


        # ---------------- RESPONSE ----------------

        return jsonify({

            "match_score": match_score,

            "resume_skills": resume_skills,

            "job_skills": job_skills,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills

        })


    except Exception as e:

        print("RESUME ERROR:", str(e))

        return jsonify({

            "error": "Something went wrong while analyzing the resume.",

            "details": str(e)

        }), 500


# ---------------- LEARNING COURSES ----------------

@app.route("/courses", methods=["GET"])
def courses():

    course_data = [

        {
            "name": "Python Programming",
            "level": "Beginner",
            "duration": "4 Weeks",
            "certificate": "Proctored Certificate Available"
        },

        {
            "name": "Data Structures & Algorithms",
            "level": "Intermediate",
            "duration": "6 Weeks",
            "certificate": "Proctored Certificate Available"
        },

        {
            "name": "Web Development",
            "level": "Beginner",
            "duration": "8 Weeks",
            "certificate": "Proctored Certificate Available"
        },

        {
            "name": "Machine Learning",
            "level": "Advanced",
            "duration": "10 Weeks",
            "certificate": "Proctored Certificate Available"
        }

    ]


    return jsonify(course_data)


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )