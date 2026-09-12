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
/* ==========================================
AI VOICE MOCK INTERVIEW
========================================== */

/*
Interview state
*/
let interviewState = {
    role: "",
    skills: [],
    currentQuestion: null,
    questionNumber: 0,
    maxQuestions: 5,
    transcript: "",
    evaluations: [],
    isListening: false,
    recognition: null
};


/*
Browser Speech Recognition
*/
const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


/*
Speak the AI question aloud
*/
function speakInterviewQuestion(question) {

    if (!("speechSynthesis" in window)) {

        console.warn(
            "Speech synthesis is not supported by this browser."
        );

        return;

    }

    window.speechSynthesis.cancel();

    const utterance =
        new SpeechSynthesisUtterance(question);

    utterance.lang = "en-IN";
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.volume = 1;

    utterance.onstart = function () {

        setInterviewStatus(
            "🔊 AI is speaking..."
        );

    };

    utterance.onend = function () {

        setInterviewStatus(
            "● Ready — Start speaking"
        );

    };

    window.speechSynthesis.speak(utterance);
}


/*
Update interview status
*/
function setInterviewStatus(message) {

    const status =
        document.getElementById(
            "interview-status-indicator"
        );

    if (status) {

        status.textContent = message;

    }

}


/*
Update question counter
*/
function updateQuestionCounter() {

    const counter =
        document.getElementById(
            "interview-question-count"
        );

    if (counter) {

        counter.textContent =
            `Question ${interviewState.questionNumber} of ${interviewState.maxQuestions}`;

    }

}


/*
Display current question
*/
function displayInterviewQuestion(questionData) {

    interviewState.currentQuestion =
        questionData;

    const questionElement =
        document.getElementById(
            "interview-question"
        );

    if (!questionElement) {

        return;

    }

    questionElement.textContent =
        questionData.question || questionData;

    updateQuestionCounter();

    /*
    Speak only the actual question.
    */
    speakInterviewQuestion(
        questionData.question || questionData
    );

}


/*
START INTERVIEW
*/
async function startMockInterview() {

    const roleInput =
        document.getElementById(
            "interview-role"
        );

    const skillsInput =
        document.getElementById(
            "interview-skills"
        );

    const role =
        roleInput.value.trim();

    const skills =
        skillsInput.value
            .split(",")
            .map(skill => skill.trim())
            .filter(Boolean);


    if (!role) {

        alert(
            "Please enter your target role."
        );

        return;

    }


    if (!skills.length) {

        alert(
            "Please enter at least one skill."
        );

        return;

    }


    /*
    Save interview state
    */
    interviewState = {

        role: role,

        skills: skills,

        currentQuestion: null,

        questionNumber: 0,

        maxQuestions: 5,

        transcript: "",

        evaluations: [],

        isListening: false,

        recognition: null

    };


    const setup =
        document.getElementById(
            "interview-setup"
        );

    const active =
        document.getElementById(
            "interview-active"
        );

    const complete =
        document.getElementById(
            "interview-complete"
        );


    setup.classList.add("hidden");

    complete.classList.add("hidden");

    active.classList.remove("hidden");


    const questionElement =
        document.getElementById(
            "interview-question"
        );

    questionElement.textContent =
        "Generating your interview...";


    setInterviewStatus(
        "⏳ Preparing interview..."
    );


    try {

        const response =
            await fetch(
                "/api/mock-interview/start",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        role: role,

                        skills: skills

                    })

                }
            );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            throw new Error(
                (
                    data.error &&
                    data.error.message
                ) ||
                data.message ||
                "Unable to start interview."
            );

        }


        if (
            !data.questions ||
            !data.questions.length
        ) {

            throw new Error(
                "The AI did not generate any interview questions."
            );

        }


        /*
        Use the first AI-generated question.
        Subsequent questions will be adaptive
        follow-ups generated from the candidate's answer.
        */

        interviewState.questionNumber = 1;


        displayInterviewQuestion(
            data.questions[0]
        );


        document.getElementById(
            "live-transcript"
        ).textContent =
            "Your spoken answer will appear here...";


        document.getElementById(
            "interview-evaluation"
        ).innerHTML = "";


        document.getElementById(
            "submit-answer-btn"
        ).disabled = true;


    }

    catch (error) {

        console.error(
            "Interview start error:",
            error
        );


        active.classList.add("hidden");

        setup.classList.remove("hidden");


        setInterviewStatus(
            "● Ready"
        );


        alert(
            error.message ||
            "Unable to start the interview."
        );

    }

}


/*
START MICROPHONE
*/
function startListening() {

    if (!SpeechRecognition) {

        alert(
            "Voice recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge."
        );

        return;

    }


    /*
    Stop AI speech before microphone starts.
    This prevents the microphone from hearing
    the AI's own voice.
    */
    if ("speechSynthesis" in window) {

        window.speechSynthesis.cancel();

    }


    /*
    Stop an existing recognition session.
    */
    if (
        interviewState.recognition
    ) {

        try {

            interviewState.recognition.stop();

        }

        catch (error) {

            console.warn(error);

        }

    }


    const recognition =
        new SpeechRecognition();


    interviewState.recognition =
        recognition;

    interviewState.isListening = true;

    interviewState.transcript = "";


    recognition.lang = "en-IN";

    recognition.continuous = false;

    recognition.interimResults = true;

    recognition.maxAlternatives = 1;


    const transcriptElement =
        document.getElementById(
            "live-transcript"
        );


    const startButton =
        document.getElementById(
            "start-speaking-btn"
        );


    const stopButton =
        document.getElementById(
            "stop-speaking-btn"
        );


    const submitButton =
        document.getElementById(
            "submit-answer-btn"
        );


    startButton.classList.add(
        "hidden"
    );

    stopButton.classList.remove(
        "hidden"
    );

    submitButton.disabled = true;


    setInterviewStatus(
        "🎤 Listening..."
    );


    recognition.onstart =
        function () {

            setInterviewStatus(
                "🎤 Listening..."
            );

        };


    recognition.onresult =
        function (event) {

            let finalTranscript = "";
            let interimTranscript = "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                const transcript =
                    event.results[i][0]
                        .transcript;


                if (
                    event.results[i].isFinal
                ) {

                    finalTranscript +=
                        transcript + " ";

                }

                else {

                    interimTranscript +=
                        transcript;

                }

            }


            interviewState.transcript =
                finalTranscript.trim();


            transcriptElement.textContent =
                (
                    interviewState.transcript ||
                    interimTranscript ||
                    "Listening..."
                );

        };


    recognition.onerror =
        function (event) {

            console.error(
                "Speech recognition error:",
                event.error
            );


            interviewState.isListening =
                false;


            startButton.classList.remove(
                "hidden"
            );

            stopButton.classList.add(
                "hidden"
            );


            if (
                event.error ===
                "not-allowed"
            ) {

                setInterviewStatus(
                    "⚠️ Microphone permission denied"
                );

                alert(
                    "Microphone permission was denied. Please allow microphone access and try again."
                );

            }

            else if (
                event.error ===
                "no-speech"
            ) {

                setInterviewStatus(
                    "⚠️ No speech detected"
                );

            }

            else {

                setInterviewStatus(
                    "⚠️ Voice recognition error"
                );

            }

        };


    recognition.onend =
        function () {

            interviewState.isListening =
                false;


            startButton.classList.remove(
                "hidden"
            );

            stopButton.classList.add(
                "hidden"
            );


            if (
                interviewState.transcript
            ) {

                submitButton.disabled =
                    false;

                setInterviewStatus(
                    "● Answer captured — Submit when ready"
                );

            }

            else {

                setInterviewStatus(
                    "● Ready — Start speaking"
                );

            }

        };


    try {

        recognition.start();

    }

    catch (error) {

        console.error(
            error
        );

        interviewState.isListening =
            false;

    }

}


/*
STOP MICROPHONE
*/
function stopListening() {

    if (
        interviewState.recognition &&
        interviewState.isListening
    ) {

        interviewState.recognition.stop();

    }

}


/*
SUBMIT ANSWER
*/
async function submitInterviewAnswer() {

    const responseText =
        interviewState.transcript.trim();


    const currentQuestion =
        interviewState.currentQuestion;


    if (!responseText) {

        alert(
            "Please answer the question using your microphone first."
        );

        return;

    }


    if (!currentQuestion) {

        alert(
            "No active interview question."
        );

        return;

    }


    const submitButton =
        document.getElementById(
            "submit-answer-btn"
        );


    const startButton =
        document.getElementById(
            "start-speaking-btn"
        );


    submitButton.disabled = true;

    startButton.disabled = true;


    setInterviewStatus(
        "⏳ AI is evaluating your answer..."
    );


    const evaluationBox =
        document.getElementById(
            "interview-evaluation"
        );


    evaluationBox.innerHTML = `
        <p>
            Evaluating your response...
        </p>
    `;


    try {

        /*
        STEP 1
        Send transcript to Gemini
        */
        const evaluationResponse =
            await fetch(
                "/api/mock-interview/evaluate",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        question:
                            currentQuestion.question ||
                            currentQuestion,

                        response:
                            responseText

                    })

                }
            );


        const evaluationData =
            await evaluationResponse.json();


        if (
            !evaluationResponse.ok ||
            !evaluationData.success
        ) {

            throw new Error(
                (
                    evaluationData.error &&
                    evaluationData.error.message
                ) ||
                evaluationData.message ||
                "Answer evaluation failed."
            );

        }


        const evaluation =
            evaluationData.evaluation;


        /*
        Store evaluation as interview evidence.
        */
        interviewState.evaluations.push(
            evaluation
        );


        /*
        Display evaluation
        */
        displayInterviewEvaluation(
            evaluation
        );


        /*
        FINAL QUESTION
        */
        if (
            interviewState.questionNumber >=
            interviewState.maxQuestions
        ) {

            finishMockInterview();

            return;

        }


        /*
        STEP 2
        Generate adaptive follow-up
        */
        setInterviewStatus(
            "🧠 Adapting next question..."
        );


        const followUpResponse =
            await fetch(
                "/api/mock-interview/follow-up",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        role:
                            interviewState.role,

                        previous_question:
                            currentQuestion.question ||
                            currentQuestion,

                        response:
                            responseText,

                        evaluation:
                            evaluation

                    })

                }
            );


        const followUpData =
            await followUpResponse.json();


        if (
            !followUpResponse.ok ||
            !followUpData.success
        ) {

            throw new Error(
                (
                    followUpData.error &&
                    followUpData.error.message
                ) ||
                followUpData.message ||
                "Could not generate the next question."
            );

        }


        /*
        Move to next question
        */
        interviewState.questionNumber++;


        interviewState.transcript = "";


        document.getElementById(
            "live-transcript"
        ).textContent =
            "Your spoken answer will appear here...";


        displayInterviewQuestion(
            followUpData.question
        );


        submitButton.disabled =
            true;


        startButton.disabled =
            false;


        setInterviewStatus(
            "● Ready — Start speaking"
        );

    }

    catch (error) {

        console.error(
            "Interview answer error:",
            error
        );


        evaluationBox.innerHTML = `

            <p class="error-message">

                ${
                    error.message ||
                    "Something went wrong while processing your answer."
                }

            </p>

        `;


        setInterviewStatus(
            "⚠️ Could not process answer"
        );


        submitButton.disabled =
            false;

    }

}


/*
DISPLAY AI EVALUATION
*/
function displayInterviewEvaluation(
    evaluation
) {

    const evaluationBox =
        document.getElementById(
            "interview-evaluation"
        );


    if (!evaluation) {

        return;

    }


    const score =
        evaluation.score ??
        evaluation.overall_score ??
        evaluation.rating;


    const strengths =
        Array.isArray(
            evaluation.strengths
        )
            ? evaluation.strengths
            : [];


    const improvements =
        Array.isArray(
            evaluation.improvements
        )
            ? evaluation.improvements
            : [];


    evaluationBox.innerHTML = `

        <h3>
            AI Evaluation
        </h3>

        ${
            score !== undefined
                ? `
                    <div class="result-item">

                        <strong>
                            📊 Score
                        </strong>

                        <p>
                            ${score}
                        </p>

                    </div>
                  `
                : ""
        }


        ${
            strengths.length
                ? `
                    <div class="result-item">

                        <strong>
                            💪 Strengths
                        </strong>

                        <p>
                            ${strengths.join(", ")}
                        </p>

                    </div>
                  `
                : ""
        }


        ${
            improvements.length
                ? `
                    <div class="result-item">

                        <strong>
                            🚀 Areas to Improve
                        </strong>

                        <p>
                            ${improvements.join(", ")}
                        </p>

                    </div>
                  `
                : ""
        }


        ${
            evaluation.feedback
                ? `
                    <div class="result-item">

                        <strong>
                            💬 Feedback
                        </strong>

                        <p>
                            ${evaluation.feedback}
                        </p>

                    </div>
                  `
                : ""
        }

    `;

}


/*
FINISH INTERVIEW
*/
function finishMockInterview() {

    if ("speechSynthesis" in window) {

        window.speechSynthesis.cancel();

    }


    setInterviewStatus(
        "✅ Interview completed"
    );


    const active =
        document.getElementById(
            "interview-active"
        );


    const complete =
        document.getElementById(
            "interview-complete"
        );


    active.classList.add(
        "hidden"
    );

    complete.classList.remove(
        "hidden"
    );


    /*
    Calculate overall score
    */
    const scores =
        interviewState.evaluations

            .map(
                evaluation =>
                    Number(
                        evaluation.score ??
                        evaluation.overall_score ??
                        evaluation.rating
                    )
            )

            .filter(
                score =>
                    Number.isFinite(score)
            );


    let averageScore = null;


    if (scores.length) {

        averageScore =
            Math.round(
                scores.reduce(
                    (sum, score) =>
                        sum + score,
                    0
                ) / scores.length
            );

    }


    const finalResult =
        document.getElementById(
            "final-interview-result"
        );


    finalResult.innerHTML = `

        <h3>
            Interview Evidence Summary
        </h3>


        ${
            averageScore !== null
                ? `
                    <div class="result-item">

                        <strong>
                            📊 Overall Interview Score
                        </strong>

                        <p>
                            ${averageScore}
                        </p>

                    </div>
                  `
                : ""
        }


        <div class="result-item">

            <strong>
                🎯 Role
            </strong>

            <p>
                ${interviewState.role}
            </p>

        </div>


        <div class="result-item">

            <strong>
                🧠 Skills Assessed
            </strong>

            <p>
                ${interviewState.skills.join(", ")}
            </p>

        </div>


        <div class="result-item">

            <strong>
                📝 Questions Completed
            </strong>

            <p>
                ${interviewState.evaluations.length}
            </p>

        </div>


        <div class="result-item">

            <strong>
                🔎 Evidence Type
            </strong>

            <p>
                AI Technical Interview Assessment
            </p>

        </div>

    `;

}


/*
END INTERVIEW EARLY
*/
function endMockInterview() {

    if (
        interviewState.recognition &&
        interviewState.isListening
    ) {

        try {

            interviewState.recognition.stop();

        }

        catch (error) {

            console.warn(error);

        }

    }


    if ("speechSynthesis" in window) {

        window.speechSynthesis.cancel();

    }


    finishMockInterview();

}


/*
RESET INTERVIEW
*/
function resetMockInterview() {

    if ("speechSynthesis" in window) {

        window.speechSynthesis.cancel();

    }


    if (
        interviewState.recognition &&
        interviewState.isListening
    ) {

        try {

            interviewState.recognition.stop();

        }

        catch (error) {

            console.warn(error);

        }

    }


    interviewState = {

        role: "",

        skills: [],

        currentQuestion: null,

        questionNumber: 0,

        maxQuestions: 5,

        transcript: "",

        evaluations: [],

        isListening: false,

        recognition: null

    };


    document
        .getElementById(
            "interview-complete"
        )
        .classList.add(
            "hidden"
        );


    document
        .getElementById(
            "interview-active"
        )
        .classList.add(
            "hidden"
        );


    document
        .getElementById(
            "interview-setup"
        )
        .classList.remove(
            "hidden"
        );


    setInterviewStatus(
        "● Ready"
    );

}