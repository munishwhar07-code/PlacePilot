import os
import re
import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

from config import Config
from services.mongodb import get_db, to_object_id
from services.planner import generate_weekly_plan, determine_prep_mode
from services.neo4j_db import get_skill_graph, seed_skill_graph, check_neo4j_status

app = Flask(__name__)
app.config.from_object(Config)

# ---------------------------------------------------------
# Helper Decorators & Context Processors
# ---------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        user = get_current_user()
        if not user:
            session.clear()
            flash("Session expired. Please log in again.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        user = get_current_user()
        if not user or not user.get("is_admin"):
            flash("Access denied: Administrative privileges required.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Retrieves current user document from MongoDB based on session."""
    if "user_id" not in session:
        return None
    db = get_db()
    if db is None:
        return None
    user_id = to_object_id(session["user_id"])
    if not user_id:
        return None
    return db.users.find_one({"_id": user_id})

@app.context_processor
def inject_global_vars():
    """Injects current date and active user into all templates."""
    user = get_current_user()
    return {
        "current_user": user,
        "current_date": datetime.date.today().strftime("%Y-%m-%d")
    }

# ---------------------------------------------------------
# Public & Authentication Routes
# ---------------------------------------------------------

@app.route("/")
def landing():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        db = get_db()
        if db is None:
            flash("Database connection error. Please try again shortly.", "danger")
            return render_template("register.html")

        # Check existing user
        if db.users.find_one({"email": email}):
            flash("An account with this email address already exists.", "warning")
            return render_template("register.html")

        # Create user document
        new_user = {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "department": "",
            "academic_year": "2nd Year",
            "known_languages": "Python, Java",
            "target_role": "Software Development Engineer (SDE)",
            "study_hours_per_day": 2.0,
            "deadline": (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d"),
            "skill_level": "Intermediate",
            "prep_mode": "Practice Mode",
            "is_admin": False,
            "onboarding_complete": False,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }

        result = db.users.insert_one(new_user)
        session["user_id"] = str(result.inserted_id)
        session["user"] = {
            "name": name,
            "email": email,
            "is_admin": False,
            "prep_mode": "Practice Mode"
        }

        flash("Registration successful! Complete your student profile to calibrate your study plan.", "success")
        return redirect(url_for("onboarding"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html")

        db = get_db()
        if db is None:
            flash("Database connection error. Ensure MongoDB is running.", "danger")
            return render_template("login.html")

        user = db.users.find_one({"email": email})
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password combination.", "danger")
            return render_template("login.html")

        # Set session
        session["user_id"] = str(user["_id"])
        session["user"] = {
            "name": user.get("name", "Student"),
            "email": user["email"],
            "is_admin": bool(user.get("is_admin", False)),
            "prep_mode": user.get("prep_mode", "Practice Mode")
        }

        flash(f"Welcome back, {user.get('name')}!", "success")
        if not user.get("onboarding_complete"):
            return redirect(url_for("onboarding"))
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for("login"))

# ---------------------------------------------------------
# Profile & Onboarding Routes
# ---------------------------------------------------------

@app.route("/onboarding", methods=["GET", "POST"])
@login_required
def onboarding():
    user = get_current_user()
    db = get_db()

    if request.method == "POST":
        department = request.form.get("department")
        academic_year = request.form.get("academic_year")
        target_role = request.form.get("target_role")
        study_hours = float(request.form.get("study_hours_per_day", 2.0))
        known_languages = request.form.get("known_languages", "Python, Java")
        deadline = request.form.get("deadline", "")
        skill_level = request.form.get("skill_level", "Intermediate")

        prep_mode = determine_prep_mode(academic_year)

        update_data = {
            "department": department,
            "academic_year": academic_year,
            "target_role": target_role,
            "study_hours_per_day": study_hours,
            "known_languages": known_languages,
            "deadline": deadline,
            "skill_level": skill_level,
            "prep_mode": prep_mode,
            "onboarding_complete": True,
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }

        db.users.update_one({"_id": user["_id"]}, {"$set": update_data})
        user.update(update_data)

        # Update session
        session["user"]["prep_mode"] = prep_mode

        # Generate initial study plan and tasks
        plan_data = generate_weekly_plan(user)
        
        # Save study plan
        plan_doc = {
            "user_id": user["_id"],
            "mode": plan_data["mode"],
            "summary": plan_data["summary"],
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }
        plan_res = db.study_plans.insert_one(plan_doc)

        # Remove old tasks if any, then insert new tasks
        db.study_tasks.delete_many({"user_id": user["_id"]})
        tasks_to_insert = []
        for t in plan_data["tasks"]:
            t["user_id"] = user["_id"]
            t["plan_id"] = plan_res.inserted_id
            tasks_to_insert.append(t)
        
        if tasks_to_insert:
            db.study_tasks.insert_many(tasks_to_insert)

        flash("Profile configured! Your adaptive weekly study plan is ready.", "success")
        return redirect(url_for("dashboard"))

    return render_template("onboarding.html", user=user, active_page="onboarding")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()
    db = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department")
        academic_year = request.form.get("academic_year")
        prep_mode = request.form.get("prep_mode")
        target_role = request.form.get("target_role")
        study_hours = float(request.form.get("study_hours_per_day", 2.0))
        known_languages = request.form.get("known_languages")
        deadline = request.form.get("deadline")
        skill_level = request.form.get("skill_level")

        update_data = {
            "name": name,
            "department": department,
            "academic_year": academic_year,
            "prep_mode": prep_mode,
            "target_role": target_role,
            "study_hours_per_day": study_hours,
            "known_languages": known_languages,
            "deadline": deadline,
            "skill_level": skill_level,
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }

        db.users.update_one({"_id": user["_id"]}, {"$set": update_data})
        session["user"]["name"] = name
        session["user"]["prep_mode"] = prep_mode

        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user, active_page="profile")

# ---------------------------------------------------------
# Dashboard Route
# ---------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    if not user.get("onboarding_complete"):
        return redirect(url_for("onboarding"))

    db = get_db()
    user_id = user["_id"]

    # Study Tasks metrics
    total_tasks_count = db.study_tasks.count_documents({"user_id": user_id})
    completed_tasks_count = db.study_tasks.count_documents({"user_id": user_id, "status": "completed"})
    pending_tasks_count = total_tasks_count - completed_tasks_count

    # Coding metrics
    total_problems_count = db.coding_problems.count_documents({})
    solved_problems_count = db.coding_drafts.count_documents({"user_id": user_id, "status": "solved"})

    # Aptitude metrics
    aptitude_attempts_count = db.quiz_attempts.count_documents({"user_id": user_id})
    latest_attempt = db.quiz_attempts.find_one({"user_id": user_id}, sort=[("created_at", -1)])

    # Average score per aptitude category for Chart.js
    categories = ["Quantitative Aptitude", "Logical Reasoning", "Verbal Ability"]
    aptitude_chart_labels = ["Quantitative", "Logical", "Verbal"]
    aptitude_chart_data = []

    for cat in categories:
        pipeline = [
            {"$match": {"user_id": user_id, "category": cat}},
            {"$group": {"_id": None, "avg_pct": {"$avg": "$percentage"}}}
        ]
        res = list(db.quiz_attempts.aggregate(pipeline))
        avg_score = round(res[0]["avg_pct"], 1) if res else 0.0
        aptitude_chart_data.append(avg_score)

    # Revision metrics
    pending_revisions_count = db.revision_entries.count_documents({"user_id": user_id, "status": "Pending"})
    recent_revisions = list(db.revision_entries.find({"user_id": user_id}).sort("created_at", -1).limit(4))

    # Recommended Next Task (First pending task, prioritized by High/Medium)
    next_task = db.study_tasks.find_one(
        {"user_id": user_id, "status": "pending"},
        sort=[("priority", 1), ("day_number", 1)]
    )

    # Pending tasks list
    pending_tasks = list(db.study_tasks.find(
        {"user_id": user_id, "status": "pending"}
    ).sort("day_number", 1).limit(5))

    return render_template(
        "dashboard.html",
        user=user,
        active_page="dashboard",
        total_tasks_count=total_tasks_count,
        completed_tasks_count=completed_tasks_count,
        pending_tasks_count=pending_tasks_count,
        total_problems_count=total_problems_count,
        solved_problems_count=solved_problems_count,
        aptitude_attempts_count=aptitude_attempts_count,
        latest_attempt=latest_attempt,
        aptitude_chart_labels=aptitude_chart_labels,
        aptitude_chart_data=aptitude_chart_data,
        pending_revisions_count=pending_revisions_count,
        recent_revisions=recent_revisions,
        next_task=next_task,
        pending_tasks=pending_tasks
    )

# ---------------------------------------------------------
# Study Plan Routes
# ---------------------------------------------------------

@app.route("/study-plan")
@login_required
def study_plan():
    user = get_current_user()
    db = get_db()
    user_id = user["_id"]

    active_filter = request.args.get("filter", "all")
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    plan = db.study_plans.find_one({"user_id": user_id}, sort=[("created_at", -1)]) or {
        "mode": user.get("prep_mode", "Practice Mode"),
        "summary": "Customized placement curriculum."
    }

    query = {"user_id": user_id}
    if active_filter == "today":
        query["due_date"] = today_str
    elif active_filter == "pending":
        query["status"] = "pending"
    elif active_filter == "completed":
        query["status"] = "completed"

    tasks = list(db.study_tasks.find(query).sort([("day_number", 1), ("priority", 1)]))

    total_count = db.study_tasks.count_documents({"user_id": user_id})
    completed_count = db.study_tasks.count_documents({"user_id": user_id, "status": "completed"})
    pending_count = total_count - completed_count
    today_count = db.study_tasks.count_documents({"user_id": user_id, "due_date": today_str})

    completion_percent = int((completed_count / total_count * 100)) if total_count > 0 else 0

    return render_template(
        "study_plan.html",
        plan=plan,
        tasks=tasks,
        active_page="study_plan",
        active_filter=active_filter,
        total_count=total_count,
        completed_count=completed_count,
        pending_count=pending_count,
        today_count=today_count,
        completion_percent=completion_percent
    )

@app.route("/study-plan/rebuild", methods=["POST"])
@login_required
def rebuild_study_plan():
    user = get_current_user()
    db = get_db()
    user_id = user["_id"]

    plan_data = generate_weekly_plan(user)

    plan_doc = {
        "user_id": user_id,
        "mode": plan_data["mode"],
        "summary": plan_data["summary"],
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "updated_at": datetime.datetime.now(datetime.timezone.utc)
    }
    plan_res = db.study_plans.insert_one(plan_doc)

    # Delete existing auto-generated tasks
    db.study_tasks.delete_many({"user_id": user_id})

    tasks_to_insert = []
    for t in plan_data["tasks"]:
        t["user_id"] = user_id
        t["plan_id"] = plan_res.inserted_id
        tasks_to_insert.append(t)

    if tasks_to_insert:
        db.study_tasks.insert_many(tasks_to_insert)

    flash(f"Study plan rebuilt successfully for {plan_data['mode']}!", "success")
    return redirect(url_for("study_plan"))

@app.route("/study-plan/task/<task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    db = get_db()
    user = get_current_user()
    t_id = to_object_id(task_id)

    task = db.study_tasks.find_one({"_id": t_id, "user_id": user["_id"]})
    if task:
        new_status = "completed" if task.get("status") != "completed" else "pending"
        completed_at = datetime.datetime.now(datetime.timezone.utc) if new_status == "completed" else None
        db.study_tasks.update_one(
            {"_id": t_id},
            {"$set": {"status": new_status, "completed_at": completed_at}}
        )

    redirect_to = request.form.get("redirect_to", "study_plan")
    if redirect_to == "dashboard":
        return redirect(url_for("dashboard"))
    return redirect(url_for("study_plan"))

@app.route("/study-plan/task/<task_id>/edit", methods=["POST"])
@login_required
def edit_task(task_id):
    db = get_db()
    user = get_current_user()
    t_id = to_object_id(task_id)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    due_date = request.form.get("due_date")
    estimated_minutes = int(request.form.get("estimated_minutes", 45))
    priority = request.form.get("priority", "Medium")

    db.study_tasks.update_one(
        {"_id": t_id, "user_id": user["_id"]},
        {"$set": {
            "title": title,
            "description": description,
            "due_date": due_date,
            "estimated_minutes": estimated_minutes,
            "priority": priority,
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }}
    )
    flash("Task details updated.", "success")
    return redirect(url_for("study_plan"))

@app.route("/study-plan/task/<task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    db = get_db()
    user = get_current_user()
    t_id = to_object_id(task_id)

    db.study_tasks.delete_one({"_id": t_id, "user_id": user["_id"]})
    flash("Study task removed.", "info")
    return redirect(url_for("study_plan"))

@app.route("/study-plan/task/add", methods=["POST"])
@login_required
def add_task():
    db = get_db()
    user = get_current_user()

    title = request.form.get("title", "").strip()
    topic = request.form.get("topic", "").strip()
    category = request.form.get("category", "Coding")
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", datetime.date.today().strftime("%Y-%m-%d"))
    estimated_minutes = int(request.form.get("estimated_minutes", 45))
    description = request.form.get("description", "").strip()

    if not title:
        flash("Task title is required.", "danger")
        return redirect(url_for("study_plan"))

    new_task = {
        "user_id": user["_id"],
        "plan_id": None,
        "day_number": 1,
        "day_label": "Custom Task",
        "due_date": due_date,
        "title": title,
        "topic": topic,
        "category": category,
        "description": description,
        "estimated_minutes": estimated_minutes,
        "priority": priority,
        "status": "pending",
        "completed_at": None,
        "created_at": datetime.datetime.now(datetime.timezone.utc)
    }

    db.study_tasks.insert_one(new_task)
    flash("Custom study task added to your schedule!", "success")
    return redirect(url_for("study_plan"))

# ---------------------------------------------------------
# Coding Practice Routes
# ---------------------------------------------------------

@app.route("/coding")
@login_required
def coding_list():
    db = get_db()
    user = get_current_user()
    user_id = user["_id"]

    search_query = request.args.get("q", "").strip()
    selected_topic = request.args.get("topic", "")
    selected_diff = request.args.get("difficulty", "")
    selected_status = request.args.get("status", "")

    query = {}
    if search_query:
        query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"topic": {"$regex": search_query, "$options": "i"}}
        ]
    if selected_topic:
        query["topic"] = selected_topic
    if selected_diff:
        query["difficulty"] = selected_diff

    all_problems = list(db.coding_problems.find(query).sort("title", 1))

    # Fetch user's drafts and completion statuses
    user_drafts = {d["problem_id"]: d for d in db.coding_drafts.find({"user_id": user_id})}

    filtered_problems = []
    solved_count = 0
    total_count = db.coding_problems.count_documents({})

    for p in all_problems:
        p_id = str(p["_id"])
        user_draft = user_drafts.get(p_id)
        is_solved = bool(user_draft and user_draft.get("status") == "solved")
        has_draft = bool(user_draft and user_draft.get("code"))

        p["user_solved"] = is_solved
        p["user_draft"] = has_draft

        if is_solved:
            solved_count += 1

        if selected_status == "solved" and not is_solved:
            continue
        elif selected_status == "unsolved" and is_solved:
            continue

        filtered_problems.append(p)

    return render_template(
        "coding_list.html",
        problems=filtered_problems,
        active_page="coding",
        search_query=search_query,
        selected_topic=selected_topic,
        selected_diff=selected_diff,
        selected_status=selected_status,
        solved_count=solved_count,
        total_count=total_count
    )

@app.route("/coding/<slug>")
@login_required
def coding_detail(slug):
    db = get_db()
    user = get_current_user()
    user_id = user["_id"]

    problem = db.coding_problems.find_one({"slug": slug})
    if not problem:
        abort(404)

    draft = db.coding_drafts.find_one({"user_id": user_id, "problem_id": str(problem["_id"])})

    return render_template(
        "coding_detail.html",
        problem=problem,
        draft=draft,
        active_page="coding"
    )

@app.route("/coding/<slug>/draft", methods=["POST"])
@login_required
def save_coding_draft(slug):
    db = get_db()
    user = get_current_user()
    user_id = user["_id"]

    problem = db.coding_problems.find_one({"slug": slug})
    if not problem:
        return jsonify({"status": "error", "message": "Problem not found"}), 404

    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python")

    db.coding_drafts.update_one(
        {"user_id": user_id, "problem_id": str(problem["_id"])},
        {"$set": {
            "code": code,
            "language": language,
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }},
        upsert=True
    )
    return jsonify({"status": "ok", "message": "Draft saved successfully!"})

@app.route("/coding/<slug>/solve", methods=["POST"])
@login_required
def solve_problem(slug):
    db = get_db()
    user = get_current_user()
    user_id = user["_id"]

    problem = db.coding_problems.find_one({"slug": slug})
    if not problem:
        abort(404)

    new_status = request.form.get("status", "solved")

    db.coding_drafts.update_one(
        {"user_id": user_id, "problem_id": str(problem["_id"])},
        {"$set": {
            "status": new_status,
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }},
        upsert=True
    )

    if new_status == "solved":
        flash(f"Congratulations! You solved '{problem['title']}'! Progress logged.", "success")
    else:
        flash(f"'{problem['title']}' marked as incomplete.", "info")

    return redirect(url_for("coding_detail", slug=slug))

# ---------------------------------------------------------
# Aptitude Practice Routes
# ---------------------------------------------------------

@app.route("/aptitude")
@login_required
def aptitude_categories():
    db = get_db()
    user = get_current_user()
    user_id = user["_id"]

    quant_count = db.aptitude_questions.count_documents({"category": "Quantitative Aptitude"})
    logic_count = db.aptitude_questions.count_documents({"category": "Logical Reasoning"})
    verbal_count = db.aptitude_questions.count_documents({"category": "Verbal Ability"})

    def get_avg(cat):
        pipeline = [
            {"$match": {"user_id": user_id, "category": cat}},
            {"$group": {"_id": None, "avg_pct": {"$avg": "$percentage"}}}
        ]
        res = list(db.quiz_attempts.aggregate(pipeline))
        return round(res[0]["avg_pct"], 1) if res else 0.0

    quant_avg = get_avg("Quantitative Aptitude")
    logic_avg = get_avg("Logical Reasoning")
    verbal_avg = get_avg("Verbal Ability")

    attempts = list(db.quiz_attempts.find({"user_id": user_id}).sort("created_at", -1))

    return render_template(
        "aptitude_categories.html",
        active_page="aptitude",
        quant_count=quant_count,
        logic_count=logic_count,
        verbal_count=verbal_count,
        quant_avg=quant_avg,
        logic_avg=logic_avg,
        verbal_avg=verbal_avg,
        attempts=attempts
    )

@app.route("/aptitude/<category>")
@login_required
def aptitude_quiz(category):
    db = get_db()
    valid_categories = ["Quantitative Aptitude", "Logical Reasoning", "Verbal Ability"]
    if category not in valid_categories:
        abort(404)

    questions = list(db.aptitude_questions.find({"category": category}))
    if not questions:
        flash("No questions found for this category yet.", "warning")
        return redirect(url_for("aptitude_categories"))

    return render_template(
        "aptitude_quiz.html",
        category=category,
        questions=questions,
        active_page="aptitude"
    )

@app.route("/aptitude/<category>/submit", methods=["POST"])
@login_required
def submit_quiz(category):
    db = get_db()
    user = get_current_user()
    user_id = user["_id"]

    questions = list(db.aptitude_questions.find({"category": category}))
    total_q = len(questions)
    score = 0
    recorded_answers = []

    for q in questions:
        q_id_str = str(q["_id"])
        selected_val = request.form.get(f"q_{q_id_str}")
        selected_opt = int(selected_val) if selected_val is not None and selected_val != "" else None
        
        is_correct = (selected_opt is not None and selected_opt == q["correct_option"])
        if is_correct:
            score += 1

        recorded_answers.append({
            "question_id": q_id_str,
            "selected_option": selected_opt,
            "is_correct": is_correct
        })

    percentage = round((score / total_q) * 100, 1) if total_q > 0 else 0.0

    attempt_doc = {
        "user_id": user_id,
        "category": category,
        "score": score,
        "total_questions": total_q,
        "percentage": percentage,
        "answers": recorded_answers,
        "created_at": datetime.datetime.now(datetime.timezone.utc)
    }

    result = db.quiz_attempts.insert_one(attempt_doc)
    flash(f"Quiz completed! You scored {score}/{total_q} ({percentage}%).", "success")
    return redirect(url_for("aptitude_result", attempt_id=str(result.inserted_id)))

@app.route("/aptitude/result/<attempt_id>")
@login_required
def aptitude_result(attempt_id):
    db = get_db()
    user = get_current_user()
    att_id = to_object_id(attempt_id)

    attempt = db.quiz_attempts.find_one({"_id": att_id, "user_id": user["_id"]})
    if not attempt:
        abort(404)

    # Reconstruct review items with questions and explanations
    review_items = []
    for ans in attempt.get("answers", []):
        q = db.aptitude_questions.find_one({"_id": to_object_id(ans["question_id"])})
        if q:
            review_items.append({
                "question": q["question"],
                "options": q["options"],
                "correct_option": q["correct_option"],
                "selected_option": ans["selected_option"],
                "is_correct": ans["is_correct"],
                "explanation": q.get("explanation", "Review the concept fundamentals.")
            })

    return render_template(
        "aptitude_result.html",
        attempt=attempt,
        review_items=review_items,
        active_page="aptitude"
    )

# ---------------------------------------------------------
# Revision Tracker Routes
# ---------------------------------------------------------

@app.route("/revision")
@login_required
def revision_tracker():
    db = get_db()
    user = get_current_user()
    user_id = user["_id"]

    active_filter = request.args.get("filter", "all")
    query = {"user_id": user_id}
    if active_filter in ["Pending", "Reviewed"]:
        query["status"] = active_filter

    entries = list(db.revision_entries.find(query).sort("revision_date", 1))

    total_count = db.revision_entries.count_documents({"user_id": user_id})
    pending_count = db.revision_entries.count_documents({"user_id": user_id, "status": "Pending"})
    reviewed_count = total_count - pending_count

    return render_template(
        "revision.html",
        entries=entries,
        active_page="revision",
        active_filter=active_filter,
        total_count=total_count,
        pending_count=pending_count,
        reviewed_count=reviewed_count
    )

@app.route("/revision/add", methods=["POST"])
@login_required
def add_revision():
    db = get_db()
    user = get_current_user()

    topic = request.form.get("topic", "").strip()
    mistake = request.form.get("mistake", "").strip()
    notes = request.form.get("notes", "").strip()
    revision_date = request.form.get("revision_date", datetime.date.today().strftime("%Y-%m-%d"))
    status = request.form.get("status", "Pending")

    if not topic or not mistake or not notes:
        flash("Topic, mistake, and notes are required fields.", "danger")
        return redirect(url_for("revision_tracker"))

    entry = {
        "user_id": user["_id"],
        "topic": topic,
        "mistake": mistake,
        "notes": notes,
        "revision_date": revision_date,
        "status": status,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "updated_at": datetime.datetime.now(datetime.timezone.utc)
    }

    db.revision_entries.insert_one(entry)
    flash("Revision topic logged successfully!", "success")
    return redirect(url_for("revision_tracker"))

@app.route("/revision/<entry_id>/edit", methods=["POST"])
@login_required
def edit_revision(entry_id):
    db = get_db()
    user = get_current_user()
    e_id = to_object_id(entry_id)

    topic = request.form.get("topic", "").strip()
    mistake = request.form.get("mistake", "").strip()
    notes = request.form.get("notes", "").strip()
    revision_date = request.form.get("revision_date")
    status = request.form.get("status", "Pending")

    db.revision_entries.update_one(
        {"_id": e_id, "user_id": user["_id"]},
        {"$set": {
            "topic": topic,
            "mistake": mistake,
            "notes": notes,
            "revision_date": revision_date,
            "status": status,
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }}
    )
    flash("Revision entry updated.", "success")
    return redirect(url_for("revision_tracker"))

@app.route("/revision/<entry_id>/toggle", methods=["POST"])
@login_required
def toggle_revision_status(entry_id):
    db = get_db()
    user = get_current_user()
    e_id = to_object_id(entry_id)

    entry = db.revision_entries.find_one({"_id": e_id, "user_id": user["_id"]})
    if entry:
        new_status = "Reviewed" if entry.get("status") != "Reviewed" else "Pending"
        db.revision_entries.update_one(
            {"_id": e_id},
            {"$set": {"status": new_status, "updated_at": datetime.datetime.now(datetime.timezone.utc)}}
        )
    return redirect(url_for("revision_tracker"))

@app.route("/revision/<entry_id>/delete", methods=["POST"])
@login_required
def delete_revision(entry_id):
    db = get_db()
    user = get_current_user()
    e_id = to_object_id(entry_id)

    db.revision_entries.delete_one({"_id": e_id, "user_id": user["_id"]})
    flash("Revision item deleted.", "info")
    return redirect(url_for("revision_tracker"))

# ---------------------------------------------------------
# Skill Dependency Explorer Routes
# ---------------------------------------------------------

@app.route("/skills-graph")
@login_required
def skills_graph():
    graph_data = get_skill_graph()
    return render_template(
        "skills_graph.html",
        graph_data=graph_data,
        active_page="skills_graph"
    )

@app.route("/skills-graph/seed", methods=["POST"])
@login_required
def seed_neo4j_route():
    success, msg = seed_skill_graph()
    if success:
        flash("Skill graph successfully synchronized!", "success")
    else:
        flash(f"Skill tree notice: {msg}", "info")
    return redirect(url_for("skills_graph"))

# ---------------------------------------------------------
# Administration Routes (Admin Only)
# ---------------------------------------------------------

@app.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()
    total_users = db.users.count_documents({})
    problems = list(db.coding_problems.find().sort("title", 1))
    questions = list(db.aptitude_questions.find().sort("category", 1))

    return render_template(
        "admin.html",
        active_page="admin",
        total_users=total_users,
        problems=problems,
        questions=questions
    )

@app.route("/admin/problem/new", methods=["GET", "POST"])
@admin_required
def admin_problem_new():
    db = get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip().lower()
        topic = request.form.get("topic")
        difficulty = request.form.get("difficulty")
        description = request.form.get("description", "").strip()
        sample_input = request.form.get("sample_input", "").strip()
        sample_output = request.form.get("sample_output", "").strip()
        constraints = request.form.get("constraints", "").strip()
        external_link = request.form.get("external_link", "").strip()
        starter_python = request.form.get("starter_python", "").strip()

        if not slug:
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()

        new_prob = {
            "title": title,
            "slug": slug,
            "topic": topic,
            "difficulty": difficulty,
            "description": description,
            "sample_input": sample_input,
            "sample_output": sample_output,
            "constraints": constraints,
            "external_link": external_link,
            "starter_codes": {
                "python": starter_python,
                "cpp": "// Implement solution\n",
                "java": "// Implement solution\n",
                "javascript": "// Implement solution\n"
            },
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }

        db.coding_problems.insert_one(new_prob)
        flash(f"Problem '{title}' added to coding library!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_problem_form.html", problem=None, active_page="admin")

@app.route("/admin/problem/<problem_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_problem_edit(problem_id):
    db = get_db()
    p_id = to_object_id(problem_id)
    problem = db.coding_problems.find_one({"_id": p_id})
    if not problem:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip().lower()
        topic = request.form.get("topic")
        difficulty = request.form.get("difficulty")
        description = request.form.get("description", "").strip()
        sample_input = request.form.get("sample_input", "").strip()
        sample_output = request.form.get("sample_output", "").strip()
        constraints = request.form.get("constraints", "").strip()
        external_link = request.form.get("external_link", "").strip()
        starter_python = request.form.get("starter_python", "").strip()

        starter_codes = problem.get("starter_codes", {})
        starter_codes["python"] = starter_python

        db.coding_problems.update_one(
            {"_id": p_id},
            {"$set": {
                "title": title,
                "slug": slug,
                "topic": topic,
                "difficulty": difficulty,
                "description": description,
                "sample_input": sample_input,
                "sample_output": sample_output,
                "constraints": constraints,
                "external_link": external_link,
                "starter_codes": starter_codes,
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            }}
        )
        flash(f"Problem '{title}' updated successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_problem_form.html", problem=problem, active_page="admin")

@app.route("/admin/problem/<problem_id>/delete", methods=["POST"])
@admin_required
def admin_problem_delete(problem_id):
    db = get_db()
    p_id = to_object_id(problem_id)
    db.coding_problems.delete_one({"_id": p_id})
    flash("Coding problem removed from library.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/aptitude/new", methods=["GET", "POST"])
@admin_required
def admin_aptitude_new():
    db = get_db()
    if request.method == "POST":
        category = request.form.get("category")
        question = request.form.get("question", "").strip()
        opt0 = request.form.get("option_0", "").strip()
        opt1 = request.form.get("option_1", "").strip()
        opt2 = request.form.get("option_2", "").strip()
        opt3 = request.form.get("option_3", "").strip()
        correct_option = int(request.form.get("correct_option", 0))
        explanation = request.form.get("explanation", "").strip()

        new_q = {
            "category": category,
            "question": question,
            "options": [opt0, opt1, opt2, opt3],
            "correct_option": correct_option,
            "explanation": explanation,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }

        db.aptitude_questions.insert_one(new_q)
        flash("Aptitude question added to library!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_aptitude_form.html", question=None, active_page="admin")

@app.route("/admin/aptitude/<question_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_aptitude_edit(question_id):
    db = get_db()
    q_id = to_object_id(question_id)
    question = db.aptitude_questions.find_one({"_id": q_id})
    if not question:
        abort(404)

    if request.method == "POST":
        category = request.form.get("category")
        q_text = request.form.get("question", "").strip()
        opt0 = request.form.get("option_0", "").strip()
        opt1 = request.form.get("option_1", "").strip()
        opt2 = request.form.get("option_2", "").strip()
        opt3 = request.form.get("option_3", "").strip()
        correct_option = int(request.form.get("correct_option", 0))
        explanation = request.form.get("explanation", "").strip()

        db.aptitude_questions.update_one(
            {"_id": q_id},
            {"$set": {
                "category": category,
                "question": q_text,
                "options": [opt0, opt1, opt2, opt3],
                "correct_option": correct_option,
                "explanation": explanation,
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            }}
        )
        flash("Aptitude question updated successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_aptitude_form.html", question=question, active_page="admin")

@app.route("/admin/aptitude/<question_id>/delete", methods=["POST"])
@admin_required
def admin_aptitude_delete(question_id):
    db = get_db()
    q_id = to_object_id(question_id)
    db.aptitude_questions.delete_one({"_id": q_id})
    flash("Aptitude question removed.", "info")
    return redirect(url_for("admin_dashboard"))

# ---------------------------------------------------------
# Custom Error Handlers
# ---------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    # Ensure indexes on startup
    get_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
