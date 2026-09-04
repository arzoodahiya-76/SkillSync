"""
SkillSync Database Layer (SQLite).

Provides persistent storage for students, resumes, competencies, evidence,
opportunities, assessments, roadmaps, and reassessment records.
"""

import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from backend.config import Config

DB_PATH = Config.BASE_DIR / "skillsync.db"


def get_db_path() -> Path:
    return DB_PATH


@contextmanager
def get_db_connection():
    """Yields an active SQLite connection with Row factory and foreign keys enabled."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initializes all database tables and seeds initial data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Students Profile
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            education TEXT,
            university TEXT,
            degree TEXT,
            branch TEXT,
            year TEXT,
            interests TEXT,
            target_role TEXT DEFAULT 'Software Engineer',
            target_industry TEXT DEFAULT 'Technology',
            github_username TEXT,
            created_at TEXT NOT NULL
        );
        """)

        # 2. Resumes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            parsed_data TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        );
        """)

        # 3. Student Competencies
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS competencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'CLAIMED', -- CLAIMED, DEVELOPING, VERIFIED, BENCHMARKED
            required_level REAL DEFAULT 4.0,       -- 1.0 to 5.0
            validated_level REAL DEFAULT 1.0,      -- 1.0 to 5.0
            confidence REAL DEFAULT 0.2,           -- 0.0 to 1.0
            evidence_summary TEXT,
            updated_at TEXT NOT NULL,
            UNIQUE (student_id, skill_name),
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        );
        """)

        # 4. Evidence Records
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            competency TEXT NOT NULL,
            evidence_type TEXT NOT NULL,          -- RESUME, THEORY_ASSESSMENT, PRACTICAL, GITHUB, etc.
            score REAL,                           -- 0.0 to 100.0
            confidence REAL NOT NULL,             -- 0.0 to 1.0
            verification_status TEXT NOT NULL,    -- UNVERIFIED, PENDING, VERIFIED
            source TEXT NOT NULL,
            explanation TEXT,
            metadata TEXT,                        -- JSON
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        );
        """)

        # 5. Opportunities / Target Roles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT DEFAULT 'Remote / Hybrid',
            description TEXT NOT NULL,
            required_skills TEXT NOT NULL,        -- JSON list
            preferred_skills TEXT NOT NULL,       -- JSON list
            criticality TEXT,                     -- JSON dict
            min_readiness_score REAL DEFAULT 60.0,
            created_at TEXT NOT NULL
        );
        """)

        # 6. Assessments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competency TEXT NOT NULL,
            title TEXT NOT NULL,
            assessment_type TEXT NOT NULL,        -- THEORY, PRACTICAL
            questions TEXT NOT NULL,              -- JSON list of questions/challenges
            passing_score REAL DEFAULT 70.0,
            created_at TEXT NOT NULL
        );
        """)

        # 7. Assessment Attempts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            assessment_id INTEGER NOT NULL,
            competency TEXT NOT NULL,
            score REAL NOT NULL,
            passed INTEGER NOT NULL,
            answers TEXT NOT NULL,                -- JSON
            attempted_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id) ON DELETE CASCADE
        );
        """)

        # 8. Skill Gaps
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_gaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            target_role TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            required_level REAL NOT NULL,
            validated_level REAL NOT NULL,
            gap_size REAL NOT NULL,
            criticality TEXT NOT NULL DEFAULT 'CRITICAL', -- CRITICAL, MODERATE, LOW
            initial_gap REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'OPEN',          -- OPEN, IN_PROGRESS, CLOSED
            updated_at TEXT NOT NULL,
            UNIQUE(student_id, target_role, skill_name),
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        );
        """)

        # 9. Roadmaps
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            target_role TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            steps TEXT NOT NULL,                  -- JSON list of roadmap steps
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(student_id, target_role, skill_name),
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        );
        """)

        _seed_default_data(conn)


def _seed_default_data(conn):
    """Seeds default student profile, opportunities, and competency assessments if empty."""
    cursor = conn.cursor()

    # Seed Default Student Profile (Demo Student: Arzoo Dahiya)
    cursor.execute("SELECT COUNT(*) FROM students;")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO students (name, email, education, university, degree, branch, year, interests, target_role, target_industry, github_username, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            "Arzoo Dahiya",
            "arzoo@skillsync.edu",
            "Bachelor of Technology",
            "Thapar Institute of Engineering & Technology",
            "B.Tech",
            "Computer Science & Engineering",
            "3rd Year",
            json.dumps(["Full Stack Development", "Cloud Architecture", "Applied AI"]),
            "Backend Python Engineer",
            "Technology & Software",
            "arzoodahiya",
            now
        ))

    # Seed Curated Opportunities
    cursor.execute("SELECT COUNT(*) FROM opportunities;")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        opportunities_data = [
            (
                "Software Engineer Intern",
                "Google",
                "Bangalore / Hyderabad",
                "Design and develop scalable cloud software systems, backend REST APIs, and distributed data pipelines.",
                json.dumps(["Python", "Data Structures", "SQL", "Git"]),
                json.dumps(["Docker", "Cloud Computing", "C++"]),
                json.dumps({"Python": "CRITICAL", "Data Structures": "CRITICAL", "SQL": "MODERATE", "Git": "MODERATE"}),
                65.0,
                now
            ),
            (
                "Backend Python Engineer",
                "SkillSync Labs",
                "Remote",
                "Architect high-throughput Flask/FastAPI microservices, manage SQL/NoSQL databases, and integrate AI APIs.",
                json.dumps(["Python", "Flask", "SQL", "REST API"]),
                json.dumps(["Docker", "AWS", "Git"]),
                json.dumps({"Python": "CRITICAL", "Flask": "CRITICAL", "SQL": "CRITICAL", "REST API": "MODERATE"}),
                70.0,
                now
            ),
            (
                "Junior Full Stack Developer",
                "Microsoft",
                "Noida / Remote",
                "Build modern, reactive user interfaces with React and connect resilient cloud-backed REST endpoints.",
                json.dumps(["JavaScript", "React", "HTML", "CSS", "SQL"]),
                json.dumps(["Node.js", "Docker", "Git"]),
                json.dumps({"JavaScript": "CRITICAL", "React": "CRITICAL", "SQL": "MODERATE"}),
                60.0,
                now
            ),
            (
                "Machine Learning Associate",
                "Amazon AWS",
                "Hyderabad / Remote",
                "Develop predictive modeling pipelines using Python, NumPy, Pandas, and machine learning architectures.",
                json.dumps(["Python", "Machine Learning", "NumPy", "Pandas"]),
                json.dumps(["SQL", "Docker", "AWS"]),
                json.dumps({"Python": "CRITICAL", "Machine Learning": "CRITICAL", "Pandas": "MODERATE"}),
                70.0,
                now
            )
        ]
        cursor.executemany("""
        INSERT INTO opportunities (title, company, location, description, required_skills, preferred_skills, criticality, min_readiness_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, opportunities_data)

    # Seed Competency Assessments (Theory & Practical)
    cursor.execute("SELECT COUNT(*) FROM assessments;")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        assessments_data = [
            # Python Theory Assessment
            (
                "Python",
                "Python Core Concepts & OOP Assessment",
                "THEORY",
                json.dumps([
                    {
                        "id": "q1",
                        "question": "What is the primary difference between a list and a tuple in Python?",
                        "options": [
                            "Lists are immutable, tuples are mutable",
                            "Lists are mutable, tuples are immutable",
                            "Lists can only store integers",
                            "Tuples are always faster at indexing by a factor of 10"
                        ],
                        "correct_index": 1,
                        "explanation": "Tuples are immutable sequences once defined, whereas lists can be dynamically modified."
                    },
                    {
                        "id": "q2",
                        "question": "Which decorator is used to define a method bound to the class rather than the instance?",
                        "options": ["@staticmethod", "@classmethod", "@property", "@binding"],
                        "correct_index": 1,
                        "explanation": "@classmethod receives the class 'cls' as the implicit first argument."
                    },
                    {
                        "id": "q3",
                        "question": "How does Python handle memory management under the hood?",
                        "options": [
                            "Manual deallocation via free()",
                            "Reference counting combined with a generational garbage collector",
                            "Stop-the-world tracing collector only",
                            "Memory is never reclaimed until process termination"
                        ],
                        "correct_index": 1,
                        "explanation": "CPython uses reference counting as its primary collector, supplemented by a cyclic generational GC."
                    }
                ]),
                70.0,
                now
            ),
            # Python Practical Assessment
            (
                "Python",
                "Python Practical: Clean Architecture & File Processing",
                "PRACTICAL",
                json.dumps([
                    {
                        "id": "p1",
                        "title": "Build a Resilient File Ingestion Filter",
                        "prompt": "Write a Python function `filter_skills(skills, forbidden)` that cleans whitespace, lowercases, and removes forbidden entries.",
                        "test_cases": [
                            {"input": {"skills": [" Python ", "Java", "c++"], "forbidden": ["c++"]}, "expected": ["python", "java"]}
                        ],
                        "criteria": "Handles edge cases, returns deduplicated clean lowercase strings."
                    }
                ]),
                75.0,
                now
            ),
            # SQL Theory Assessment
            (
                "SQL",
                "Relational Databases & SQL Querying Assessment",
                "THEORY",
                json.dumps([
                    {
                        "id": "sql_q1",
                        "question": "What is the difference between WHERE and HAVING clauses in SQL?",
                        "options": [
                            "WHERE filters rows before aggregation; HAVING filters aggregated groups",
                            "HAVING filters rows before aggregation; WHERE filters groups",
                            "WHERE can only be used with numeric values",
                            "They are completely interchangeable synonyms"
                        ],
                        "correct_index": 0,
                        "explanation": "WHERE filters source rows prior to GROUP BY aggregation; HAVING filters post-aggregation groups."
                    },
                    {
                        "id": "sql_q2",
                        "question": "Which JOIN returns all rows from the left table and matched rows from the right table?",
                        "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "CROSS JOIN"],
                        "correct_index": 1,
                        "explanation": "A LEFT JOIN preserves every row from the left table, populating NULLs for non-matching right rows."
                    }
                ]),
                70.0,
                now
            ),
            # Data Structures Theory Assessment
            (
                "Data Structures",
                "Data Structures & Complexity Fundamentals",
                "THEORY",
                json.dumps([
                    {
                        "id": "dsa_q1",
                        "question": "What is the average time complexity of lookups in a hash map with a good hash function?",
                        "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
                        "correct_index": 0,
                        "explanation": "Hash table average lookup time is O(1) constant time assuming low collision rate."
                    },
                    {
                        "id": "dsa_q2",
                        "question": "Which data structure operates on a First-In, First-Out (FIFO) principle?",
                        "options": ["Stack", "Queue", "Binary Search Tree", "Max Heap"],
                        "correct_index": 1,
                        "explanation": "A Queue is a FIFO data structure (elements inserted at tail and dequeued from head)."
                    }
                ]),
                70.0,
                now
            ),
            # Flask Theory Assessment
            (
                "Flask",
                "RESTful Web Services with Flask Assessment",
                "THEORY",
                json.dumps([
                    {
                        "id": "flask_q1",
                        "question": "Which method in Flask is used to return a JSON response with the application/json MIME type?",
                        "options": ["json.dumps()", "jsonify()", "render_template()", "response.json()"],
                        "correct_index": 1,
                        "explanation": "Flask's jsonify() serializes data to JSON and sets the Content-Type header to application/json."
                    },
                    {
                        "id": "flask_q2",
                        "question": "How are HTTP methods specified for a Flask route decorator?",
                        "options": [
                            "@app.route('/path', methods=['GET', 'POST'])",
                            "@app.route('/path', verbs=['GET'])",
                            "@app.route('/path', http_methods='GET,POST')",
                            "@app.route('/path').allow('GET')"
                        ],
                        "correct_index": 0,
                        "explanation": "The 'methods' list argument specifies acceptable HTTP methods on the route decorator."
                    }
                ]),
                70.0,
                now
            )
        ]
        cursor.executemany("""
        INSERT INTO assessments (competency, title, assessment_type, questions, passing_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """, assessments_data)


# Auto-initialize database schema when module is imported
init_db()
