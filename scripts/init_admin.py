import sys
import os
import getpass
import datetime
from werkzeug.security import generate_password_hash

# Add parent directory to path so config and services can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.mongodb import get_db

def init_admin():
    """Initializes or promotes a user to administrator with secure password hashing."""
    print("========================================")
    print(" PlacePilot - Administrator Setup Tool")
    print("========================================")
    
    db = get_db()
    if db is None:
        print("[Error] Cannot connect to MongoDB. Ensure MongoDB is running.")
        sys.exit(1)

    email = input("Enter Admin Email (e.g., admin@college.edu): ").strip()
    if not email or "@" not in email:
        print("[Error] Invalid email address.")
        sys.exit(1)

    existing_user = db.users.find_one({"email": email})
    
    if existing_user:
        print(f"\nUser '{email}' already exists.")
        confirm = input("Promote this user to Administrator? (y/n): ").strip().lower()
        if confirm == 'y':
            db.users.update_one(
                {"email": email},
                {"$set": {"is_admin": True, "updated_at": datetime.datetime.now(datetime.timezone.utc)}}
            )
            print(f"[Success] User '{email}' is now an Administrator!")
        else:
            print("Operation cancelled.")
    else:
        name = input("Enter Admin Full Name: ").strip() or "Administrator"
        pwd = getpass.getpass("Enter Admin Password (min 6 characters): ")
        if len(pwd) < 6:
            print("[Error] Password must be at least 6 characters long.")
            sys.exit(1)
        pwd_confirm = getpass.getpass("Confirm Admin Password: ")
        if pwd != pwd_confirm:
            print("[Error] Passwords do not match.")
            sys.exit(1)

        admin_doc = {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(pwd),
            "department": "Placement & Training Cell",
            "academic_year": "Faculty / Administrator",
            "known_languages": "Python, Java, C++",
            "target_role": "Placement Coordinator",
            "study_hours_per_day": 2.0,
            "deadline": "",
            "skill_level": "Advanced",
            "prep_mode": "Placement Sprint Mode",
            "is_admin": True,
            "onboarding_complete": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }
        db.users.insert_one(admin_doc)
        print(f"\n[Success] Created new Administrator account: {email}")

if __name__ == "__main__":
    init_admin()
