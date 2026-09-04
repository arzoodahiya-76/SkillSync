import csv
import os


def load_skills():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(BASE_DIR, "data", "skills.csv")

    skills = []

    with open(file_path, "r") as file:
        reader = csv.reader(file)

        for row in reader:
            for skill in row:
                skill = skill.strip().lower()

                if skill:
                    skills.append(skill)

    return list(set(skills))


def analyze_skills(user_skills):
    available_skills = load_skills()

    user_skills = [
        skill.strip().lower()
        for skill in user_skills
        if skill.strip()
    ]

    matched_skills = []
    missing_skills = []

    for skill in available_skills:

        if skill in user_skills:
            matched_skills.append(skill)

        else:
            missing_skills.append(skill)

    recommendations = []

    for skill in missing_skills[:5]:
        recommendations.append(
            f"Consider learning {skill.title()} to improve your profile."
        )

    return {
        "your_skills": user_skills,
        "matched_skills": matched_skills,
        "skill_gaps": missing_skills,
        "recommendations": recommendations
    }