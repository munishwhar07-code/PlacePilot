import sys
import os

# Add parent directory to path so config and services can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.neo4j_db import seed_skill_graph, check_neo4j_status
from config import Config

def main():
    print("--- PlacePilot Neo4j Skill Graph Seeding ---")
    print(f"Target URI: {Config.NEO4J_URI} (User: {Config.NEO4J_USERNAME})")
    
    connected, msg = check_neo4j_status()
    if not connected:
        print(f"\n[Warning] Neo4j is not connected: {msg}")
        print("\nTo enable Neo4j for the Skill Dependency Explorer:")
        print("1. Start your local Neo4j Desktop / Neo4j service (e.g. at bolt://localhost:7687).")
        print("2. Ensure username and password in .env match your Neo4j configuration.")
        print("3. Re-run this script: python scripts/seed_neo4j.py")
        print("\nNote: PlacePilot will continue to function fully for study plans, coding, quizzes, and dashboard even if Neo4j is offline.")
        return

    success, result_msg = seed_skill_graph()
    if success:
        print(f"\n[Success] {result_msg}")
    else:
        print(f"\n[Error] {result_msg}")

if __name__ == "__main__":
    main()
