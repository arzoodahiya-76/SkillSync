/* ==========================================
SHOW SECTION
========================================== */

function showSection(sectionId) {

    document
        .querySelectorAll(".interactive-section")
        .forEach(section => {

            section.classList.add("hidden");

        });


    const selectedSection =
        document.getElementById(sectionId);


    if (!selectedSection) {

        console.error(
            "Section not found:",
            sectionId
        );

        return;

    }


    selectedSection.classList.remove(
        "hidden"
    );


    setTimeout(() => {

        selectedSection.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }, 100);

}


/* ==========================================
SKILL ANALYSIS
========================================== */

async function analyzeSkills() {

    const skillsInput = document
        .getElementById("skills-input")
        .value;


    const resultBox = document
        .getElementById("skills-result");


    if (!skillsInput.trim()) {

        resultBox.innerHTML = `
            <p class="error-message">
                Please enter at least one skill.
            </p>
        `;

        return;

    }


    resultBox.innerHTML = `
        <p>Analyzing your skills...</p>
    `;


    try {

        const response = await fetch(

            "/analyze-skills",

            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body: JSON.stringify({

                    skills: skillsInput

                })

            }

        );


        const data =
            await response.json();


        if (data.success) {

            resultBox.innerHTML = `

                <h3>
                    Your Skill Intelligence Report
                </h3>


                <div class="result-item">

                    <strong>
                        🎯 Best Matching Career Role
                    </strong>

                    <p>
                        ${data.best_matching_role}
                    </p>

                </div>


                <div class="result-item">

                    <strong>
                        📊 Match Score
                    </strong>

                    <p>
                        ${data.job_match_score}%
                    </p>

                </div>


                <div class="result-item">

                    <strong>
                        ⭐ Competency Level
                    </strong>

                    <p>
                        ${data.competency_level}
                    </p>

                </div>


                <div class="result-item">

                    <strong>
                        💪 Your Strengths
                    </strong>

                    <p>
                        ${
                            data.strengths.length
                            ? data.strengths.join(", ")
                            : "Keep building your core skills."
                        }
                    </p>

                </div>


                <div class="result-item">

                    <strong>
                        🚀 Recommended Skills
                    </strong>

                    <p>
                        ${
                            data.recommended_skills.join(", ")
                        }
                    </p>

                </div>


                <div class="result-item">

                    <strong>
                        📚 Skill Gaps
                    </strong>

                    <p>
                        ${
                            data.missing_skills.join(", ")
                        }
                    </p>

                </div>

            `;

        }

        else {

            resultBox.innerHTML = `

                <p class="error-message">

                    ${(data.error && data.error.message) || data.message || "Analysis failed."}

                </p>

            `;

        }

    }

    catch (error) {

        console.error(error);

        resultBox.innerHTML = `

            <p class="error-message">

                Something went wrong while
                analyzing your skills.

            </p>

        `;

    }

}


/* ==========================================
RESUME ANALYSIS
========================================== */

async function analyzeResume() {

    const fileInput =
        document.getElementById(
            "resume-file"
        );


    const jobDescription =
        document.getElementById(
            "job-description"
        ).value;


    const resultBox =
        document.getElementById(
            "resume-result"
        );


    if (!fileInput.files.length) {

        resultBox.innerHTML = `
            <p class="error-message">
                Please upload your resume.
            </p>
        `;

        return;

    }


    if (!jobDescription.trim()) {

        resultBox.innerHTML = `
            <p class="error-message">
                Please enter a job description.
            </p>
        `;

        return;

    }


    resultBox.innerHTML = `

        <p>
            Analyzing your resume...
        </p>

    `;


    const formData =
        new FormData();


    formData.append(

        "resume",

        fileInput.files[0]

    );


    formData.append(

        "job_description",

        jobDescription

    );


    try {

        const response = await fetch(

            "/analyze-resume",

            {

                method: "POST",

                body: formData

            }

        );


        const data =
            await response.json();


        if (data.success) {

            resultBox.innerHTML = `

                <h3>
                    Resume Intelligence Report
                </h3>


                <div class="result-item">

                    <strong>
                        📊 Job Match Score
                    </strong>

                    <p>
                        ${data.match_score}%
                    </p>

                </div>


                <div class="result-item">

                    <strong>
                        💪 Skills Found in Resume
                    </strong>

                    <p>
                        ${
                            data.resume_skills.join(", ")
                            || "No recognized skills found."
                        }
                    </p>

                </div>


                <div class="result-item">

                    <strong>
                        🎯 Job Required Skills
                    </strong>

                    <p>
                        ${
                            data.job_skills.join(", ")
                            || "No recognized skills found."
                        }
                    </p>

                </div>


                <div class="result-item">

                    <strong>
                        🚀 Missing Skills
                    </strong>

                    <p>
                        ${
                            data.missing_skills.join(", ")
                            || "Great! No major gaps detected."
                        }
                    </p>

                </div>


                ${data.strengths && data.strengths.length ? `
                <div class="result-item">

                    <strong>
                        ⭐ Key Strengths
                    </strong>

                    <p>
                        ${Array.isArray(data.strengths) ? data.strengths.join(", ") : data.strengths}
                    </p>

                </div>
                ` : ""}


                ${((data.recommendations && data.recommendations.length) || (data.improvement_recommendations && data.improvement_recommendations.length)) ? `
                <div class="result-item">

                    <strong>
                        💡 Improvement Recommendations
                    </strong>

                    <p>
                        ${Array.isArray(data.recommendations || data.improvement_recommendations) ? (data.recommendations || data.improvement_recommendations).join("<br>") : (data.recommendations || data.improvement_recommendations)}
                    </p>

                </div>
                ` : ""}

            `;

        }

        else {

            resultBox.innerHTML = `

                <p class="error-message">

                    ${(data.error && data.error.message) || data.message || "Resume analysis failed."}

                </p>

            `;

        }

    }

    catch (error) {

        console.error(error);

        resultBox.innerHTML = `

            <p class="error-message">

                Resume analysis failed.

            </p>

        `;

    }

}


/* ==========================================
LEARNING PATH
========================================== */

function showLearningPath() {

    const skill =
        document.getElementById(
            "learning-skill"
        ).value;


    const resultBox =
        document.getElementById(
            "learning-result"
        );


    if (!skill) {

        resultBox.innerHTML = `
            <p class="error-message">
                Please select a skill.
            </p>
        `;

        return;

    }


    const learningPaths = {

        "Python": [
            "Python Fundamentals",
            "Functions and OOP",
            "Data Structures",
            "File Handling",
            "Projects",
            "Assessment & Certificate"
        ],

        "Java": [
            "Java Fundamentals",
            "OOP",
            "Collections",
            "Exception Handling",
            "Projects",
            "Assessment & Certificate"
        ],

        "C++": [
            "C++ Fundamentals",
            "Pointers",
            "OOP",
            "STL",
            "Data Structures & Algorithms",
            "Assessment & Certificate"
        ],

        "JavaScript": [
            "JavaScript Basics",
            "DOM Manipulation",
            "ES6",
            "Async JavaScript",
            "Projects",
            "Assessment"
        ],

        "Data Structures": [
            "Arrays",
            "Linked Lists",
            "Stacks and Queues",
            "Trees",
            "Graphs",
            "Practice Problems"
        ],

        "Machine Learning": [
            "Python for ML",
            "NumPy and Pandas",
            "Data Visualization",
            "Supervised Learning",
            "Model Evaluation",
            "Projects"
        ],

        "Web Development": [
            "HTML",
            "CSS",
            "JavaScript",
            "Backend Development",
            "Databases",
            "Full Stack Project"
        ]

    };


    const path =
        learningPaths[skill];


    let html = `

        <h3>
            ${skill} Learning Path
        </h3>

        <div class="learning-path">

    `;


    path.forEach((step, index) => {

        html += `

            <div class="learning-step">

                <span>
                    ${index + 1}
                </span>

                <p>
                    ${step}
                </p>

            </div>

        `;

    });


    html += `
        </div>
    `;


    resultBox.innerHTML = html;

}