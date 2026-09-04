function showSection(sectionId) {

    // Hide all interactive sections

    document.querySelectorAll(".interactive-section").forEach(section => {

        section.classList.add("hidden");

    });


    // Show selected section

    const selectedSection = document.getElementById(sectionId);

    selectedSection.classList.remove("hidden");


    // Smooth scroll

    selectedSection.scrollIntoView({

        behavior: "smooth",

        block: "center"

    });

}

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

        const response = await fetch("/analyze-skills", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                skills: skillsInput

            })

        });


        const data = await response.json();


        if (data.success) {

            resultBox.innerHTML = `

                <h3>Your Skill Analysis</h3>

                <div class="result-item">

                    <strong>Your Skills:</strong>

                    <p>${data.user_skills.join(", ")}</p>

                </div>


                <div class="result-item">

                    <strong>Recommended Skills:</strong>

                    <p>${data.recommended_skills.join(", ")}</p>

                </div>


                <div class="result-item">

                    <strong>Missing Skills:</strong>

                    <p>${data.missing_skills.join(", ")}</p>

                </div>

            `;

        }

        else {

            resultBox.innerHTML = `

                <p class="error-message">

                    ${data.message}

                </p>

            `;

        }

    }

    catch (error) {

        console.error(error);

        resultBox.innerHTML = `

            <p class="error-message">

                Something went wrong while analyzing skills.

            </p>

        `;

    }

}

function analyzeResume() {

    const fileInput = document.getElementById("resume-file");

    const jobDescription = document
        .getElementById("job-description")
        .value;

    const resultBox = document
        .getElementById("resume-result");


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

        <h3>Resume Analysis</h3>

        <div class="result-item">

            <strong>Resume:</strong>

            <p>${fileInput.files[0].name}</p>

        </div>


        <div class="result-item">

            <strong>Job Description:</strong>

            <p>Job description successfully received.</p>

        </div>


        <div class="result-item">

            <strong>Next Step:</strong>

            <p>
                Resume analysis is ready to be connected
                with the SkillSync backend.
            </p>

        </div>

    `;

}

function showLearningPath() {

    const skill = document
        .getElementById("learning-skill")
        .value;

    const resultBox = document
        .getElementById("learning-result");


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

            "Python Basics",
            "Functions and OOP",
            "Data Structures",
            "File Handling",
            "Projects",
            "Assessment & Certificate"

        ],

        "Java": [

            "Java Fundamentals",
            "Object-Oriented Programming",
            "Collections",
            "Exception Handling",
            "Projects",
            "Assessment & Certificate"

        ],

        "C++": [

            "C++ Fundamentals",
            "Pointers",
            "Object-Oriented Programming",
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
            "Assessment & Certificate"

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


    const path = learningPaths[skill];


    let html = `

        <h3>${skill} Learning Path</h3>

        <div class="learning-path">

    `;


    path.forEach((step, index) => {

        html += `

            <div class="learning-step">

                <span>${index + 1}</span>

                <p>${step}</p>

            </div>

        `;

    });


    html += `</div>`;


    resultBox.innerHTML = html;

}