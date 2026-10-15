import os
import sys
import unittest
import datetime

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from services.mongodb import get_db, to_object_id
from services.planner import generate_weekly_plan, determine_prep_mode
from services.neo4j_db import check_neo4j_status, get_skill_graph
from config import Config

class PlacePilotTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()
        cls.db = get_db()
        assert cls.db is not None, "MongoDB must be running for tests."

    def setUp(self):
        # Create a fresh client and unique test user email for this test case
        self.client = app.test_client()
        self.test_email = f"test_{int(datetime.datetime.now().timestamp()*1000)}@college.edu"
        self.test_password = "Password123"

    def tearDown(self):
        # Clean up any test records created
        if self.db is not None:
            user = self.db.users.find_one({"email": self.test_email})
            if user:
                user_id = user["_id"]
                self.db.study_plans.delete_many({"user_id": user_id})
                self.db.study_tasks.delete_many({"user_id": user_id})
                self.db.coding_drafts.delete_many({"user_id": user_id})
                self.db.quiz_attempts.delete_many({"user_id": user_id})
                self.db.revision_entries.delete_many({"user_id": user_id})
                self.db.users.delete_one({"_id": user_id})

    # -------------------------------------------------------------
    # 1. Test Registration, Login, and Session Authentication
    # -------------------------------------------------------------
    def test_01_registration_and_login(self):
        # Test successful registration
        reg_response = self.client.post("/register", data={
            "name": "Test Student",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        }, follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        self.assertIn(b"Step 1 of 1: Profile Initialization", reg_response.data)

        # Verify password is encrypted, not plain text
        user = self.db.users.find_one({"email": self.test_email})
        self.assertIsNotNone(user)
        self.assertNotEqual(user["password_hash"], self.test_password)

        # Log out
        logout_response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(logout_response.status_code, 200)

        # Test duplicate registration rejection while unauthenticated
        dup_response = self.client.post("/register", data={
            "name": "Test Duplicate",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        }, follow_redirects=True)
        self.assertIn(b"already exists", dup_response.data)

        # Test Login
        login_response = self.client.post("/login", data={
            "email": self.test_email,
            "password": self.test_password
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b"Welcome", login_response.data)

    # -------------------------------------------------------------
    # 2. Test Onboarding and Study Plan Rule-Based Generation
    # -------------------------------------------------------------
    def test_02_onboarding_and_study_plan_generation(self):
        # Register and log in
        self.client.post("/register", data={
            "name": "Placement Candidate",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        }, follow_redirects=True)

        # Submit Onboarding with 3rd Year (Practice Mode) & 3.0 Hours/Day
        onboarding_res = self.client.post("/onboarding", data={
            "department": "Computer Science & Engineering",
            "academic_year": "3rd Year",
            "target_role": "Software Development Engineer (SDE)",
            "study_hours_per_day": "3.0",
            "known_languages": "Python, Java",
            "deadline": "2026-12-31",
            "skill_level": "Intermediate"
        }, follow_redirects=True)
        self.assertEqual(onboarding_res.status_code, 200)
        self.assertIn(b"Dashboard", onboarding_res.data)

        # Verify study tasks were generated in MongoDB
        user = self.db.users.find_one({"email": self.test_email})
        tasks = list(self.db.study_tasks.find({"user_id": user["_id"]}))
        self.assertGreater(len(tasks), 0)
        
        # Verify mode rules
        self.assertEqual(user["prep_mode"], "Practice Mode")
        plan = self.db.study_plans.find_one({"user_id": user["_id"]})
        self.assertIsNotNone(plan)
        self.assertEqual(plan["mode"], "Practice Mode")

    # -------------------------------------------------------------
    # 3. Test Study Task Toggle, Reschedule & Custom Tasks
    # -------------------------------------------------------------
    def test_03_task_completion_and_crud(self):
        self.client.post("/register", data={
            "name": "Task Tester",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        }, follow_redirects=True)

        self.client.post("/onboarding", data={
            "department": "Information Technology",
            "academic_year": "2nd Year",
            "target_role": "Frontend Developer",
            "study_hours_per_day": "2.0",
            "known_languages": "JavaScript, Python",
            "deadline": "2026-11-30",
            "skill_level": "Beginner"
        }, follow_redirects=True)

        user = self.db.users.find_one({"email": self.test_email})
        task = self.db.study_tasks.find_one({"user_id": user["_id"]})
        self.assertIsNotNone(task)
        self.assertEqual(task["status"], "pending")

        # Toggle task to completed
        toggle_res = self.client.post(f"/study-plan/task/{task['_id']}/toggle", follow_redirects=True)
        self.assertEqual(toggle_res.status_code, 200)
        updated_task = self.db.study_tasks.find_one({"_id": task["_id"]})
        self.assertEqual(updated_task["status"], "completed")

        # Add custom task
        add_res = self.client.post("/study-plan/task/add", data={
            "title": "Solve 5 LeetCode Mediums",
            "topic": "Arrays & Strings",
            "category": "Coding",
            "priority": "High",
            "due_date": "2026-10-20",
            "estimated_minutes": "60",
            "description": "Two pointers and sliding window problems"
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        custom_task = self.db.study_tasks.find_one({"user_id": user["_id"], "title": "Solve 5 LeetCode Mediums"})
        self.assertIsNotNone(custom_task)

        # Delete task
        del_res = self.client.post(f"/study-plan/task/{custom_task['_id']}/delete", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        deleted_task = self.db.study_tasks.find_one({"_id": custom_task["_id"]})
        self.assertIsNone(deleted_task)

    # -------------------------------------------------------------
    # 4. Test Coding Practice, Drafts, and Solving
    # -------------------------------------------------------------
    def test_04_coding_practice_module(self):
        self.client.post("/register", data={
            "name": "Coder User",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        }, follow_redirects=True)

        # View coding list
        list_res = self.client.get("/coding")
        self.assertEqual(list_res.status_code, 200)
        self.assertIn(b"Two Sum", list_res.data)

        # View problem detail
        detail_res = self.client.get("/coding/two-sum")
        self.assertEqual(detail_res.status_code, 200)
        self.assertIn(b"Two Sum", detail_res.data)

        # Save code draft
        draft_res = self.client.post("/coding/two-sum/draft", json={
            "code": "def twoSum(nums, target): return [0, 1]",
            "language": "python"
        })
        self.assertEqual(draft_res.status_code, 200)
        json_data = draft_res.get_json()
        self.assertEqual(json_data["status"], "ok")

        # Mark problem as solved
        solve_res = self.client.post("/coding/two-sum/solve", data={"status": "solved"}, follow_redirects=True)
        self.assertEqual(solve_res.status_code, 200)

        user = self.db.users.find_one({"email": self.test_email})
        problem = self.db.coding_problems.find_one({"slug": "two-sum"})
        saved_draft = self.db.coding_drafts.find_one({"user_id": user["_id"], "problem_id": str(problem["_id"])})
        self.assertIsNotNone(saved_draft)
        self.assertEqual(saved_draft["status"], "solved")

    # -------------------------------------------------------------
    # 5. Test Aptitude Quizzes and Real Score Calculation
    # -------------------------------------------------------------
    def test_05_aptitude_scoring(self):
        self.client.post("/register", data={
            "name": "Aptitude Tester",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        }, follow_redirects=True)

        user = self.db.users.find_one({"email": self.test_email})
        category = "Quantitative Aptitude"
        questions = list(self.db.aptitude_questions.find({"category": category}))
        self.assertGreater(len(questions), 0)

        # Build answers payload where question 0 is correct, rest incorrect
        form_data = {}
        for idx, q in enumerate(questions):
            q_id = str(q["_id"])
            if idx == 0:
                form_data[f"q_{q_id}"] = q["correct_option"]
            else:
                wrong_opt = (q["correct_option"] + 1) % 4
                form_data[f"q_{q_id}"] = wrong_opt

        submit_res = self.client.post(f"/aptitude/{category}/submit", data=form_data, follow_redirects=True)
        self.assertEqual(submit_res.status_code, 200)

        # Check recorded attempt in MongoDB
        attempt = self.db.quiz_attempts.find_one({"user_id": user["_id"], "category": category})
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt["score"], 1)
        self.assertEqual(attempt["total_questions"], len(questions))
        expected_pct = round((1 / len(questions)) * 100, 1)
        self.assertEqual(attempt["percentage"], expected_pct)

    # -------------------------------------------------------------
    # 6. Test Revision Tracker CRUD Operations
    # -------------------------------------------------------------
    def test_06_revision_tracker_crud(self):
        self.client.post("/register", data={
            "name": "Revision Tester",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        }, follow_redirects=True)
        user = self.db.users.find_one({"email": self.test_email})

        # CREATE
        add_res = self.client.post("/revision/add", data={
            "topic": "Kadane Algorithm",
            "mistake": "Failed when all numbers in array are negative",
            "notes": "Initialize max_sum to nums[0] instead of 0",
            "revision_date": "2026-10-18",
            "status": "Pending"
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)

        entry = self.db.revision_entries.find_one({"user_id": user["_id"], "topic": "Kadane Algorithm"})
        self.assertIsNotNone(entry)
        self.assertEqual(entry["status"], "Pending")

        # EDIT
        edit_res = self.client.post(f"/revision/{entry['_id']}/edit", data={
            "topic": "Kadane Algorithm (Updated)",
            "mistake": "Negative array edge cases",
            "notes": "Remember O(1) space and O(N) time trade-off",
            "revision_date": "2026-10-19",
            "status": "Pending"
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)
        updated_entry = self.db.revision_entries.find_one({"_id": entry["_id"]})
        self.assertEqual(updated_entry["topic"], "Kadane Algorithm (Updated)")

        # TOGGLE STATUS
        toggle_res = self.client.post(f"/revision/{entry['_id']}/toggle", follow_redirects=True)
        self.assertEqual(toggle_res.status_code, 200)
        toggled_entry = self.db.revision_entries.find_one({"_id": entry["_id"]})
        self.assertEqual(toggled_entry["status"], "Reviewed")

        # DELETE
        del_res = self.client.post(f"/revision/{entry['_id']}/delete", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertIsNone(self.db.revision_entries.find_one({"_id": entry["_id"]}))

    # -------------------------------------------------------------
    # 7. Test Admin Operations and Role-Based Access Control
    # -------------------------------------------------------------
    def test_07_admin_crud_and_access_control(self):
        # 1. Regular student should be DENIED admin access
        self.client.post("/register", data={
            "name": "Regular Student",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        }, follow_redirects=True)

        admin_res = self.client.get("/admin", follow_redirects=True)
        self.assertIn(b"Access denied", admin_res.data)

        # 2. Promote user to Admin in DB and log in
        user = self.db.users.find_one({"email": self.test_email})
        self.db.users.update_one({"_id": user["_id"]}, {"$set": {"is_admin": True}})
        
        # Re-login so session gets admin flag
        self.client.get("/logout")
        self.client.post("/login", data={"email": self.test_email, "password": self.test_password}, follow_redirects=True)

        admin_page_res = self.client.get("/admin")
        self.assertEqual(admin_page_res.status_code, 200)
        self.assertIn(b"System Administration", admin_page_res.data)

        # 3. Admin CREATE Coding Problem
        new_prob_res = self.client.post("/admin/problem/new", data={
            "title": "Admin Test Problem",
            "slug": "admin-test-problem",
            "topic": "Arrays & Strings",
            "difficulty": "Medium",
            "description": "Test problem description",
            "sample_input": "[1, 2, 3]",
            "sample_output": "6",
            "constraints": "1 <= N <= 100",
            "external_link": "https://leetcode.com",
            "starter_python": "def test(): pass"
        }, follow_redirects=True)
        self.assertEqual(new_prob_res.status_code, 200)

        created_prob = self.db.coding_problems.find_one({"slug": "admin-test-problem"})
        self.assertIsNotNone(created_prob)

        # 4. Admin DELETE Coding Problem
        del_prob_res = self.client.post(f"/admin/problem/{created_prob['_id']}/delete", follow_redirects=True)
        self.assertEqual(del_prob_res.status_code, 200)
        self.assertIsNone(self.db.coding_problems.find_one({"slug": "admin-test-problem"}))

    # -------------------------------------------------------------
    # 8. Test Neo4j Skill Graph Query and Fallback Mechanism
    # -------------------------------------------------------------
    def test_08_neo4j_graceful_handling(self):
        # Even if Neo4j is offline or disconnected, get_skill_graph should NOT crash.
        # It must return a structured dictionary with connected: bool.
        graph_data = get_skill_graph()
        self.assertIsInstance(graph_data, dict)
        self.assertIn("connected", graph_data)
        self.assertIn("nodes", graph_data)
        self.assertIn("edges", graph_data)
        self.assertIn("message", graph_data)

if __name__ == "__main__":
    unittest.main()
