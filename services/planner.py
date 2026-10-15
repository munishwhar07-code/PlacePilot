import datetime
from bson import ObjectId

def determine_prep_mode(academic_year):
    """
    Determines the default preparation mode based on academic year:
    - 1st/2nd Year -> Foundation Mode
    - 3rd Year -> Practice Mode
    - 4th / Final Year -> Placement Sprint Mode
    """
    year_str = str(academic_year).lower()
    if "1" in year_str or "first" in year_str or "2" in year_str or "second" in year_str:
        return "Foundation Mode"
    elif "3" in year_str or "third" in year_str:
        return "Practice Mode"
    elif "4" in year_str or "fourth" in year_str or "final" in year_str:
        return "Placement Sprint Mode"
    return "Practice Mode"

def generate_weekly_plan(user):
    """
    Generates a structured 7-day study plan customized for the user.
    Takes into account:
    - Mode (Foundation, Practice, Placement Sprint)
    - Target Role (SDE, Frontend, Backend, Data Analyst, Cloud/DevOps)
    - Available Study Hours per day
    - Skill Level (Beginner, Intermediate, Advanced)
    - Known Languages
    """
    mode = user.get("prep_mode") or determine_prep_mode(user.get("academic_year", "3rd Year"))
    role = user.get("target_role", "Software Development Engineer (SDE)")
    hours = float(user.get("study_hours_per_day") or 2.0)
    skill_level = user.get("skill_level", "Intermediate")
    languages = user.get("known_languages", "Python, Java")
    
    # Task count scaling based on hours
    if hours <= 2.0:
        tasks_per_day = 2
        minutes_per_task = int((hours * 60) / 2)
    elif hours <= 4.0:
        tasks_per_day = 3
        minutes_per_task = int((hours * 60) / 3)
    else:
        tasks_per_day = 4
        minutes_per_task = int((hours * 60) / 4)

    tasks_pool = _get_mode_curriculum(mode, role, skill_level, languages, minutes_per_task)

    plan_summary = f"{mode} customized for {role} ({skill_level} level) with {hours} hr(s)/day."
    
    # Generate tasks for 7 days
    generated_tasks = []
    day_names = ["Day 1 - Monday", "Day 2 - Tuesday", "Day 3 - Wednesday", 
                 "Day 4 - Thursday", "Day 5 - Friday", "Day 6 - Saturday", "Day 7 - Sunday"]
    
    today = datetime.date.today()
    
    for day_idx in range(7):
        day_date = today + datetime.timedelta(days=day_idx)
        day_label = day_names[day_idx]
        
        # Pick tasks from pool for this day
        day_tasks = tasks_pool.get(day_idx + 1, [])
        for task_info in day_tasks[:tasks_per_day]:
            task_doc = {
                "day_number": day_idx + 1,
                "day_label": day_label,
                "due_date": day_date.strftime("%Y-%m-%d"),
                "title": task_info["title"],
                "topic": task_info["topic"],
                "category": task_info["category"],
                "description": task_info["description"],
                "estimated_minutes": task_info.get("estimated_minutes", minutes_per_task),
                "priority": task_info.get("priority", "Medium"),
                "status": "pending",
                "completed_at": None,
                "created_at": datetime.datetime.now(datetime.timezone.utc)
            }
            generated_tasks.append(task_doc)
            
    return {
        "mode": mode,
        "summary": plan_summary,
        "tasks": generated_tasks
    }

def _get_mode_curriculum(mode, role, skill_level, languages, minutes_per_task):
    """Returns a curated 7-day curriculum based on mode and target role."""
    primary_lang = languages.split(",")[0].strip() if languages else "Python"
    
    if mode == "Foundation Mode":
        return {
            1: [
                {"title": f"Master {primary_lang} Control Flow & Loops", "topic": "Programming Basics", "category": "Coding", 
                 "description": f"Write programs practicing nested loops, conditionals, and functions in {primary_lang}.", "priority": "High"},
                {"title": "Number Systems & Divisibility Aptitude", "topic": "Quantitative Aptitude", "category": "Aptitude", 
                 "description": "Learn prime factorization, HCF/LCM, and divisibility rules. Solve 10 questions.", "priority": "Medium"},
                {"title": "Introduction to 1D Arrays", "topic": "Data Structures", "category": "Coding", 
                 "description": "Understand memory allocation, indexing, traversal, and reversal of arrays.", "priority": "Low"}
            ],
            2: [
                {"title": "String Traversal & In-Place Reversal", "topic": "Arrays & Strings", "category": "Coding", 
                 "description": "Practice checking palindromes and reversing vowels in a string.", "priority": "High"},
                {"title": "Percentages & Profit-Loss Formulas", "topic": "Quantitative Aptitude", "category": "Aptitude", 
                 "description": "Memorize fraction-to-percentage conversions and solve basic profit/loss problems.", "priority": "Medium"},
                {"title": "Elevator Pitch: 60-Second Self-Introduction", "topic": "Communication Practice", "category": "Soft Skills", 
                 "description": "Draft and record your 60-second professional self-introduction.", "priority": "Low"}
            ],
            3: [
                {"title": "Linear Search vs Binary Search Concept", "topic": "Searching Algorithms", "category": "Coding", 
                 "description": "Implement linear search and discover why binary search requires sorted arrays.", "priority": "High"},
                {"title": "Blood Relations & Family Tree Puzzles", "topic": "Logical Reasoning", "category": "Aptitude", 
                 "description": "Master generation diagrams to quickly solve coded blood relations.", "priority": "Medium"},
                {"title": f"Object-Oriented Basics in {primary_lang}", "topic": "Programming Basics", "category": "Core CS", 
                 "description": "Understand classes, objects, constructors, and encapsulation.", "priority": "Low"}
            ],
            4: [
                {"title": "Selection Sort and Bubble Sort", "topic": "Sorting Algorithms", "category": "Coding", 
                 "description": "Implement sorting manually and analyze why time complexity is O(N^2).", "priority": "High"},
                {"title": "Reading Comprehension & Vocabulary Roots", "topic": "Verbal Ability", "category": "Aptitude", 
                 "description": "Practice 2 reading comprehension passages and note 10 new gre-level words.", "priority": "Medium"},
                {"title": "Time Complexity: Big-O Primer", "topic": "Algorithm Analysis", "category": "Core CS", 
                 "description": "Learn to calculate time and space complexity for simple loops and recursion.", "priority": "Low"}
            ],
            5: [
                {"title": "Introduction to Hash Maps / Dictionaries", "topic": "Hashing", "category": "Coding", 
                 "description": "Solve frequency counter problems (Two Sum, Character counting) using hash maps.", "priority": "High"},
                {"title": "Ratio, Proportion & Variations", "topic": "Quantitative Aptitude", "category": "Aptitude", 
                 "description": "Solve 10 questions on compound ratios and mixture problems.", "priority": "Medium"},
                {"title": "Active Listening & Group Discussion Tips", "topic": "Communication Practice", "category": "Soft Skills", 
                 "description": "Read guidelines on constructive initiation and summarizing in GD rounds.", "priority": "Low"}
            ],
            6: [
                {"title": "Recursion Fundamentals: Factorial & Fibonacci", "topic": "Recursion", "category": "Coding", 
                 "description": "Identify base cases, recursive steps, and draw call stack diagrams.", "priority": "High"},
                {"title": "Direction Sense & Distance Tests", "topic": "Logical Reasoning", "category": "Aptitude", 
                 "description": "Solve 8 spatial and compass direction puzzles with Pythagorean theorem.", "priority": "Medium"},
                {"title": "Weekly Revision of Code & Mistakes", "topic": "Revision", "category": "Review", 
                 "description": "Review all problems attempted this week and log mistakes in Revision Tracker.", "priority": "Medium"}
            ],
            7: [
                {"title": "Take Foundation Aptitude Quiz", "topic": "Aptitude Quiz", "category": "Aptitude", 
                 "description": "Attempt a mixed 15-question quiz on Quant, Logic, and Verbal.", "priority": "High"},
                {"title": "Solve 2 Easy Array Problems on PlacePilot", "topic": "Coding Practice", "category": "Coding", 
                 "description": "Complete Two Sum and Valid Palindrome in the coding editor.", "priority": "Medium"},
                {"title": "Plan Next Week's Milestones", "topic": "Planning", "category": "Review", 
                 "description": "Reflect on week's progress and identify topics needing extra focus.", "priority": "Low"}
            ]
        }
    elif mode == "Practice Mode":
        role_task_3 = _get_role_specific_task(role, 3)
        role_task_5 = _get_role_specific_task(role, 5)
        return {
            1: [
                {"title": "Binary Search on Answer & Rotated Arrays", "topic": "Searching & Sorting", "category": "Coding", 
                 "description": "Solve Search in Rotated Sorted Array and find lower/upper bounds.", "priority": "High"},
                {"title": "Time, Speed, Distance & Trains", "topic": "Quantitative Aptitude", "category": "Aptitude", 
                 "description": "Master relative speed, average speed, and train-platform crossing formulas.", "priority": "Medium"},
                {"title": "SQL Joins, Group By & Aggregate Queries", "topic": "SQL & DBMS", "category": "Core CS", 
                 "description": "Practice INNER, LEFT, RIGHT joins and HAVING clause queries on sample tables.", "priority": "High"}
            ],
            2: [
                {"title": "Linked List: Reversal & Cycle Detection", "topic": "Linked Lists", "category": "Coding", 
                 "description": "Implement Floyd's Tortoise and Hare cycle detection and iterative list reversal.", "priority": "High"},
                {"title": "Syllogisms & Venn Diagram Deductions", "topic": "Logical Reasoning", "category": "Aptitude", 
                 "description": "Solve categorical syllogism problems using Venn diagrams and rule-based logic.", "priority": "Medium"},
                {"title": "OS Process vs Thread & Scheduling", "topic": "Operating Systems", "category": "Core CS", 
                 "description": "Revise CPU scheduling algorithms (Round Robin, SJF) and IPC concepts.", "priority": "Medium"}
            ],
            3: [
                {"title": "Stack: Valid Parentheses & Monotonic Stack", "topic": "Stacks & Queues", "category": "Coding", 
                 "description": "Implement Valid Parentheses and understand Next Greater Element pattern.", "priority": "High"},
                role_task_3,
                {"title": "Work, Pipes & Cisterns", "topic": "Quantitative Aptitude", "category": "Aptitude", 
                 "description": "Solve unit-work and LCM method problems for rate of work and filling pipes.", "priority": "Medium"}
            ],
            4: [
                {"title": "Two-Pointer & Sliding Window Techniques", "topic": "Arrays & Strings", "category": "Coding", 
                 "description": "Solve Longest Substring Without Repeating Characters and Kadane's algorithm.", "priority": "High"},
                {"title": "Computer Networks: TCP vs UDP & OSI Layers", "topic": "Computer Networks", "category": "Core CS", 
                 "description": "Review TCP 3-way handshake, DNS resolution, IP addressing, and HTTP/HTTPS.", "priority": "High"},
                {"title": "Sentence Correction & Subject-Verb Agreement", "topic": "Verbal Ability", "category": "Aptitude", 
                 "description": "Identify common grammatical traps in sentence correction exercises.", "priority": "Medium"}
            ],
            5: [
                {"title": "Hashing: Group Anagrams & Longest Consecutive", "topic": "Hashing", "category": "Coding", 
                 "description": "Optimize lookup queries to O(1) using hash sets and sorted key maps.", "priority": "High"},
                role_task_5,
                {"title": "Seating Arrangement: Linear & Circular", "topic": "Logical Reasoning", "category": "Aptitude", 
                 "description": "Practice multi-variable linear and circular arrangement puzzles with constraints.", "priority": "Medium"}
            ],
            6: [
                {"title": "DBMS Normalization & ACID Properties", "topic": "SQL & DBMS", "category": "Core CS", 
                 "description": "Revise 1NF, 2NF, 3NF, BCNF and transaction isolation levels.", "priority": "High"},
                {"title": "Resume Project Deep-Dive & STAR Framing", "topic": "Resume & Projects", "category": "Soft Skills", 
                 "description": "Frame your top 2 academic projects using Situation, Task, Action, Result (STAR).", "priority": "High"},
                {"title": "Weekly Revision in Revision Tracker", "topic": "Revision Tracker", "category": "Review", 
                 "description": "Log all edge cases and tricky bugs encountered during the week.", "priority": "Medium"}
            ],
            7: [
                {"title": "Timed Comprehensive Aptitude Quiz", "topic": "Aptitude Quiz", "category": "Aptitude", 
                 "description": "Complete a full 20-minute timed quiz covering Quant, Logic, and Verbal.", "priority": "High"},
                {"title": "Solve 2 Medium Coding Problems on PlacePilot", "topic": "Coding Practice", "category": "Coding", 
                 "description": "Implement Kadane's Algorithm and Min Stack in the coding editor.", "priority": "High"},
                {"title": "Mock Technical Self-Check", "topic": "Mock Interview", "category": "Review", 
                 "description": "Answer 5 standard OOP, OS, and DBMS interview questions aloud.", "priority": "Medium"}
            ]
        }
    else:  # Placement Sprint Mode
        role_task_2 = _get_role_specific_task(role, 2)
        role_task_4 = _get_role_specific_task(role, 4)
        return {
            1: [
                {"title": "High-Frequency Coding: Interval & Array Problems", "topic": "Coding Revision", "category": "Coding", 
                 "description": "Solve Merge Intervals and Maximum Subarray with optimal O(N) complexity.", "priority": "High"},
                {"title": "Speed Aptitude Sprint: 15 Questions in 15 Mins", "topic": "Timed Aptitude", "category": "Aptitude", 
                 "description": "Practice rapid mental math shortcuts for percentages, ratios, and averages.", "priority": "High"},
                {"title": "Top 20 Core CS Interview Rapid Fire", "topic": "Technical Interview Questions", "category": "Core CS", 
                 "description": "Review virtual memory, indexing vs full table scan, deadlock conditions, and REST principles.", "priority": "High"}
            ],
            2: [
                {"title": "Tree & Graph Traversal Revision", "topic": "Coding Revision", "category": "Coding", 
                 "description": "Revise BFS, DFS, Level Order Traversal, and recursion call stack limits.", "priority": "High"},
                role_task_2,
                {"title": "Critical Path & Coding Puzzles", "topic": "Logical Reasoning", "category": "Aptitude", 
                 "description": "Solve classic interview puzzles (2 eggs problem, burning ropes, water jugs).", "priority": "Medium"}
            ],
            3: [
                {"title": "System Design & Architecture Basics", "topic": "Technical Interview Questions", "category": "Core CS", 
                 "description": "Learn fundamentals of Load Balancers, Caching (Redis), CDN, and Horizontal scaling.", "priority": "High"},
                {"title": "Data Interpretation & Chart Analysis", "topic": "Quantitative Aptitude", "category": "Aptitude", 
                 "description": "Analyze complex bar charts, pie graphs, and tables with speed calculations.", "priority": "Medium"},
                {"title": "HR Questions: Tell Me About Yourself & Strengths", "topic": "HR Preparation", "category": "Soft Skills", 
                 "description": "Rehearse answers to 'Why should we hire you?' and 'Greatest weakness' with constructive framing.", "priority": "High"}
            ],
            4: [
                {"title": "Dynamic Programming & Recursion Patterns", "topic": "Coding Revision", "category": "Coding", 
                 "description": "Understand 0/1 Knapsack, Coin Change, and Memoization vs Tabulation trade-offs.", "priority": "High"},
                role_task_4,
                {"title": "Verbal: Para Jumbles & Critical Reasoning", "topic": "Verbal Ability", "category": "Aptitude", 
                 "description": "Practice sentence rearrangement techniques and assumption-strengthen questions.", "priority": "Medium"}
            ],
            5: [
                {"title": "Full-Length Company Placement Simulation Test", "topic": "Mock Test", "category": "Aptitude", 
                 "description": "Take full-length mock containing 30 aptitude questions and 2 coding challenges.", "priority": "High"},
                {"title": "HR Scenario: Conflict Resolution & Leadership", "topic": "HR Preparation", "category": "Soft Skills", 
                 "description": "Formulate answers for team conflict, tight deadlines, and failure handling using STAR.", "priority": "High"},
                {"title": "Company Research & Question Preparation", "topic": "HR Preparation", "category": "Soft Skills", 
                 "description": "Prepare 3 thoughtful questions to ask the interviewer at the end of the round.", "priority": "Medium"}
            ],
            6: [
                {"title": "Rapid Coding Bug Fix & Edge Case Defense", "topic": "Coding Revision", "category": "Coding", 
                 "description": "Test integer overflow, null pointers, empty inputs, and duplicate element cases.", "priority": "High"},
                {"title": "Comprehensive Revision Tracker Deep-Dive", "topic": "Revision Tracker", "category": "Review", 
                 "description": "Review all past recorded mistakes in Revision Tracker and mark solved ones as Reviewed.", "priority": "High"},
                {"title": "Peer / Mirror Mock Interview", "topic": "Mock Interviews", "category": "Soft Skills", 
                 "description": "Simulate a 45-minute live technical interview with a peer or in front of a mirror.", "priority": "High"}
            ],
            7: [
                {"title": "Final Confidence Sprint & Formula Sheet Review", "topic": "Final Review", "category": "Review", 
                 "description": "Review formula cheatsheet for Quant and quick syntax reference for coding.", "priority": "High"},
                {"title": "Rest & Mindset Optimization", "topic": "Mental Readiness", "category": "Soft Skills", 
                 "description": "Ensure sound sleep, check interview attire, verify documents, and stay calm.", "priority": "Medium"},
                {"title": "Check Off All Weekly Tasks", "topic": "Study Plan", "category": "Review", 
                 "description": "Ensure all weekly tasks are marked completed and celebrate preparation milestones.", "priority": "Low"}
            ]
        }

def _get_role_specific_task(role, day):
    """Provides role-specialized tasks for targeted placement preparation."""
    role_lower = role.lower()
    if "front" in role_lower or "ui" in role_lower:
        if day in (2, 3):
            return {"title": "Frontend: Event Loop, Closures & DOM Optimization", "topic": "Frontend Core", "category": "Core CS", 
                    "description": "Understand microtasks vs macrotasks, prototypical inheritance, and debounce/throttle.", "priority": "High"}
        else:
            return {"title": "Frontend: Component Lifecycle & State Management", "topic": "Frontend Architecture", "category": "Core CS", 
                    "description": "Build a stateful component pattern, discuss reconciliation and CSS Box Model.", "priority": "High"}
    elif "back" in role_lower:
        if day in (2, 3):
            return {"title": "Backend: REST API Design & HTTP Status Codes", "topic": "API Design", "category": "Core CS", 
                    "description": "Design idempotent endpoints, discuss idempotency keys, JWT auth, and rate limiting.", "priority": "High"}
        else:
            return {"title": "Backend: Database Indexing, B-Trees & Caching", "topic": "System Design", "category": "Core CS", 
                    "description": "Analyze clustered vs non-clustered indexes, Redis cache eviction, and connection pools.", "priority": "High"}
    elif "data" in role_lower or "analyst" in role_lower:
        if day in (2, 3):
            return {"title": "Data: Window Functions & Advanced SQL Queries", "topic": "Data Analytics", "category": "Core CS", 
                    "description": "Practice RANK(), DENSE_RANK(), PARTITION BY, and running total queries in SQL.", "priority": "High"}
        else:
            return {"title": "Data: Statistical Inference & Data Wrangling", "topic": "Statistics & Analytics", "category": "Core CS", 
                    "description": "Review standard deviation, p-values, hypothesis testing, and missing value strategies.", "priority": "High"}
    elif "cloud" in role_lower or "devops" in role_lower:
        if day in (2, 3):
            return {"title": "DevOps: Dockerfile Writing & Containerization", "topic": "DevOps Primitives", "category": "Core CS", 
                    "description": "Write multi-stage Dockerfiles, understand layers, volumes, and network bridging.", "priority": "High"}
        else:
            return {"title": "DevOps: CI/CD Pipelines & Linux Shell Scripting", "topic": "Automation", "category": "Core CS", 
                    "description": "Write Bash scripts for log parsing and understand GitHub Actions / Jenkins pipelines.", "priority": "High"}
    else:  # SDE / Software Engineer general
        if day in (2, 3):
            return {"title": "SDE: Object-Oriented Design & SOLID Principles", "topic": "OOP & Software Design", "category": "Core CS", 
                    "description": "Apply Single Responsibility, Open-Closed, Liskov, Interface Segregation, and Dependency Inversion.", "priority": "High"}
        else:
            return {"title": "SDE: Low-Level Design (Parking Lot / Library)", "topic": "Object-Oriented Design", "category": "Core CS", 
                    "description": "Draft class diagrams and design patterns (Singleton, Factory, Observer) for a system.", "priority": "High"}
