# PlacePilot — Adaptive Placement Preparation System

**PlacePilot** is a full-stack Python Flask web application designed for college students preparing for campus recruitment drives. It dynamically calibrates learning plans based on the student's academic year, target role, available daily study bandwidth, and current performance across coding, core CS, and aptitude competencies.

---

## 🌟 Key Features

1. **Adaptive Study Planner (Rule-Based)**:
   - **Foundation Mode (2nd Year)**: Programming fundamentals, basic arrays/strings, elementary quantitative aptitude, and professional communication.
   - **Practice Mode (3rd Year)**: Core DSA (trees, graphs, stacks, queues), SQL & DBMS, OS & Computer Networks, and project STAR framing.
   - **Placement Sprint Mode (Final Year)**: High-frequency coding patterns, timed company aptitude tests, core CS rapid-fire, and HR behavioral mocks.
   - Automatic generation of weekly tasks adjusted for daily study hours (1–8+ hours/day).
   - Task completion toggles, rescheduling modals, priority levels, and custom task creation.

2. **Placement Coding Library & Embedded CodeMirror Editor**:
   - 18 curated problems across 6 core interview areas (Arrays & Strings, Searching & Sorting, Hashing, Linked Lists, Stacks & Queues, Basic Recursion).
   - Embedded CodeMirror editor supporting Python, C++, Java, and JavaScript.
   - Starter code templates, sample input/output display, draft saving, and safe sample test validation without arbitrary server execution.
   - Genuine external practice links (LeetCode / GeeksForGeeks).

3. **Aptitude & Reasoning Practice Engine**:
   - 3 categories: **Quantitative Aptitude**, **Logical Reasoning**, and **Verbal Ability**.
   - 18 original multiple-choice questions with automated server-side score calculation.
   - Question-by-question review screens showing correct answers and detailed solution explanations.
   - Attempt history and percentage trends saved in MongoDB.

4. **Student Dashboard & Analytics**:
   - Academic details and preparation mode badge.
   - Real-time MongoDB metrics: tasks completed, coding problems solved, latest aptitude score, and pending revisions.
   - Interactive **Chart.js** charts for task status distribution and category-wise aptitude averages.
   - Recommended next task banner to guide immediate study action.

5. **Revision Tracker**:
   - Persistent mistake and conceptual trap log with full CRUD operations.
   - Attributes: Topic, Mistake or Difficulty, Correct Approach or Notes, Target Revision Date, and Status (`Pending` / `Reviewed`).

6. **Neo4j Skill Dependency Explorer**:
   - Graph representation of computer science concepts and directional `PREREQUISITE_FOR` relationships.
   - Interactive **Vis.js Network** visualization with node category coloring, zooming, panning, and concept inspector.
   - **Honest Offline Handling**: If Neo4j service is offline or unconfigured, displays a clear informational status banner and setup guide while keeping all other PlacePilot features 100% operational.

7. **Role-Based Administration**:
   - Protected admin portal (`/admin`) for placement coordinators and faculty administrators.
   - Full CRUD operations for Coding Problems and Aptitude Questions.
   - Interactive CLI tool (`scripts/init_admin.py`) for initializing or promoting administrators securely.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Flask 3.1
- **Database (Primary)**: MongoDB 8.0 with PyMongo
- **Graph Database (Skills)**: Neo4j with official Python driver (`neo4j`)
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons
- **Visualizations**: Chart.js 4.4, Vis.js Network 9.1
- **Code Editor**: CodeMirror 5.65 (Eclipse theme, multi-language modes)
- **Security**: Werkzeug password hashing (PBKDF2/SHA-256), session management, parameterized Cypher queries

---

## 📁 Project Structure

```
PlacePilot/
├── app.py                      # Flask application instance, routes, and error handlers
├── config.py                   # Environment configuration class
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable templates
├── .env                        # Active environment configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # System documentation and execution guide
├── services/
│   ├── mongodb.py              # MongoDB connection singleton, collection helpers, and indexes
│   ├── planner.py              # Rule-based 3-mode study planner algorithm
│   └── neo4j_db.py             # Neo4j graph queries and parameterized Cypher seeds
├── templates/
│   ├── base.html               # Shared responsive navy layout with sidebar
│   ├── landing.html            # Public landing and features showcase
│   ├── login.html              # Authentication sign-in
│   ├── register.html           # Student registration
│   ├── onboarding.html         # Profile calibration questionnaire
│   ├── profile.html            # Profile view and update
│   ├── dashboard.html          # Student dashboard and Chart.js analytics
│   ├── study_plan.html         # Weekly tasks, filters, and rescheduling
│   ├── coding_list.html        # Coding library with topic/difficulty filters
│   ├── coding_detail.html      # CodeMirror editor, drafts, and sample tests
│   ├── aptitude_categories.html# Aptitude categories and score history
│   ├── aptitude_quiz.html      # Interactive multiple-choice quiz
│   ├── aptitude_result.html    # Detailed solution breakdown and explanations
│   ├── revision.html           # Revision tracker CRUD
│   ├── skills_graph.html       # Neo4j interactive skill dependency graph
│   ├── admin.html              # Administrator management portal
│   ├── admin_problem_form.html # Problem create/edit form
│   ├── admin_aptitude_form.html# Question create/edit form
│   ├── 404.html                # Custom Not Found error page
│   └── 500.html                # Custom Server Error page
├── static/
│   ├── css/
│   │   └── style.css           # Custom dark-navy design system and responsive styles
│   └── js/
│       └── main.js             # Mobile toggles, flash dismissals, and modals
├── scripts/
│   ├── seed_mongodb.py         # Seeds 18 problems, 18 questions, and default admin
│   ├── seed_neo4j.py           # Seeds skill nodes and prerequisite graph in Neo4j
│   └── init_admin.py           # Interactive CLI tool to create/promote admin accounts
└── tests/
    └── test_app.py             # Unit and integration test suite (8 test cases)
```

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- MongoDB Server 6.0+ (Running locally on `localhost:27017` or MongoDB Atlas URI)
- (Optional) Neo4j Desktop or Server 5.x+ (at `bolt://localhost:7687`)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` if not already present:
```bash
# In Windows PowerShell:
Copy-Item .env.example .env
```
Ensure your database URIs match your local configuration:
```ini
SECRET_KEY=placepilot-secure-secret-key-2026
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=placepilot
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
ADMIN_EMAIL=admin@placepilot.edu
ADMIN_PASSWORD=Admin@PlacePilot2026
```

### 4. Seed MongoDB
Run the database seed script to populate the 18 curated coding problems, 18 aptitude questions, and the default administrator account:
```bash
python scripts/seed_mongodb.py
```

### 5. Seed Neo4j Skill Graph (Optional)
If your Neo4j service is running, populate the skills prerequisite graph:
```bash
python scripts/seed_neo4j.py
```
*(If Neo4j is not running, the application will display an informative banner on `/skills-graph` without interrupting other features.)*

### 6. Run the Application
Start the Flask development server:
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 🔑 Demonstration Accounts

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Administrator** | `admin@placepilot.edu` | `Admin@PlacePilot2026` | Full platform + Admin management (`/admin`) |
| **New Student** | Register any email on `/register` | (Self-selected) | Student dashboard & study plan |

To create or promote an admin account via CLI at any time:
```bash
python scripts/init_admin.py
```

---

## 🧪 Automated Testing

PlacePilot includes a comprehensive test suite covering registration, authentication, study plan generation, task completion, coding draft persistence, aptitude scoring, revision CRUD, role-based admin access, and Neo4j fallback:

```bash
python -m unittest tests/test_app.py -v
```

All 8 test suites pass cleanly with 100% database verification.
"# PlacePilot" 
