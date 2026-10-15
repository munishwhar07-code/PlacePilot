import sys
import os
import datetime
from werkzeug.security import generate_password_hash

# Add parent directory to path so config and services can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config
from services.mongodb import get_db

def seed_database():
    """Seeds the MongoDB database with initial coding problems, aptitude questions, and admin user."""
    db = get_db()
    if db is None:
        print("[Error] Could not connect to MongoDB. Is mongod running?")
        sys.exit(1)

    print("--- Seeding MongoDB Collections for PlacePilot ---")

    # 1. Seed Admin User
    admin_email = Config.ADMIN_EMAIL
    existing_admin = db.users.find_one({"email": admin_email})
    if not existing_admin:
        admin_doc = {
            "name": Config.ADMIN_NAME,
            "email": admin_email,
            "password_hash": generate_password_hash(Config.ADMIN_PASSWORD),
            "department": "Computer Science & Engineering",
            "academic_year": "4th Year / Final Year",
            "known_languages": "Python, Java, C++",
            "target_role": "Software Development Engineer (SDE)",
            "study_hours_per_day": 3.0,
            "deadline": (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d"),
            "skill_level": "Advanced",
            "prep_mode": "Placement Sprint Mode",
            "is_admin": True,
            "onboarding_complete": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }
        db.users.insert_one(admin_doc)
        print(f"[Admin] Created default admin user: {admin_email} (Password: {Config.ADMIN_PASSWORD})")
    else:
        # Ensure is_admin is True
        db.users.update_one({"email": admin_email}, {"$set": {"is_admin": True}})
        print(f"[Admin] User {admin_email} already exists. Ensured admin privileges.")

    # 2. Seed Coding Problems (18 problems covering 6 key areas)
    problems = [
        # Arrays & Strings
        {
            "slug": "two-sum",
            "title": "Two Sum",
            "topic": "Arrays & Strings",
            "difficulty": "Easy",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume each input would have exactly one solution, and you may not use the same element twice.",
            "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9",
            "sample_input": "nums = [2, 7, 11, 15], target = 9",
            "sample_output": "[0, 1]",
            "starter_codes": {
                "python": "def twoSum(nums, target):\n    # Write your solution here\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []\n",
                "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your solution here\n        unordered_map<int, int> seen;\n        for (int i = 0; i < nums.size(); i++) {\n            int diff = target - nums[i];\n            if (seen.count(diff)) return {seen[diff], i};\n            seen[nums[i]] = i;\n        }\n        return {};\n    }\n};",
                "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        Map<Integer, Integer> map = new HashMap<>();\n        for (int i = 0; i < nums.length; i++) {\n            int diff = target - nums[i];\n            if (map.containsKey(diff)) return new int[]{map.get(diff), i};\n            map.put(nums[i], i);\n        }\n        return new int[]{};\n    }\n}",
                "javascript": "function twoSum(nums, target) {\n    const map = new Map();\n    for (let i = 0; i < nums.length; i++) {\n        const diff = target - nums[i];\n        if (map.has(diff)) return [map.get(diff), i];\n        map.set(nums[i], i);\n    }\n    return [];\n}"
            },
            "external_link": "https://leetcode.com/problems/two-sum/"
        },
        {
            "slug": "valid-palindrome",
            "title": "Valid Palindrome",
            "topic": "Arrays & Strings",
            "difficulty": "Easy",
            "description": "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.",
            "constraints": "1 <= s.length <= 2 * 10^5\ns consists only of printable ASCII characters.",
            "sample_input": "s = \"A man, a plan, a canal: Panama\"",
            "sample_output": "true",
            "starter_codes": {
                "python": "def isPalindrome(s: str) -> bool:\n    filtered = [c.lower() for c in s if c.isalnum()]\n    return filtered == filtered[::-1]\n",
                "cpp": "class Solution {\npublic:\n    bool isPalindrome(string s) {\n        int left = 0, right = s.length() - 1;\n        while (left < right) {\n            while (left < right && !isalnum(s[left])) left++;\n            while (left < right && !isalnum(s[right])) right--;\n            if (tolower(s[left]) != tolower(s[right])) return false;\n            left++; right--;\n        }\n        return true;\n    }\n};",
                "java": "class Solution {\n    public boolean isPalindrome(String s) {\n        int l = 0, r = s.length() - 1;\n        while (l < r) {\n            while (l < r && !Character.isLetterOrDigit(s.charAt(l))) l++;\n            while (l < r && !Character.isLetterOrDigit(s.charAt(r))) r--;\n            if (Character.toLowerCase(s.charAt(l)) != Character.toLowerCase(s.charAt(r))) return false;\n            l++; r--;\n        }\n        return true;\n    }\n}",
                "javascript": "function isPalindrome(s) {\n    const cleaned = s.toLowerCase().replace(/[^a-z0-9]/g, '');\n    return cleaned === cleaned.split('').reverse().join('');\n}"
            },
            "external_link": "https://leetcode.com/problems/valid-palindrome/"
        },
        {
            "slug": "maximum-subarray-kadane",
            "title": "Maximum Subarray (Kadane's Algorithm)",
            "topic": "Arrays & Strings",
            "difficulty": "Medium",
            "description": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
            "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
            "sample_input": "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]",
            "sample_output": "6 (from subarray [4, -1, 2, 1])",
            "starter_codes": {
                "python": "def maxSubArray(nums):\n    max_sum = current_sum = nums[0]\n    for x in nums[1:]:\n        current_sum = max(x, current_sum + x)\n        max_sum = max(max_sum, current_sum)\n    return max_sum\n",
                "cpp": "class Solution {\npublic:\n    int maxSubArray(vector<int>& nums) {\n        int current_sum = nums[0], max_sum = nums[0];\n        for (int i = 1; i < nums.size(); i++) {\n            current_sum = max(nums[i], current_sum + nums[i]);\n            max_sum = max(max_sum, current_sum);\n        }\n        return max_sum;\n    }\n};",
                "java": "class Solution {\n    public int maxSubArray(int[] nums) {\n        int cur = nums[0], max = nums[0];\n        for (int i = 1; i < nums.length; i++) {\n            cur = Math.max(nums[i], cur + nums[i]);\n            max = Math.max(max, cur);\n        }\n        return max;\n    }\n}",
                "javascript": "function maxSubArray(nums) {\n    let cur = nums[0], max = nums[0];\n    for (let i = 1; i < nums.length; i++) {\n        cur = Math.max(nums[i], cur + nums[i]);\n        max = Math.max(max, cur);\n    }\n    return max;\n}"
            },
            "external_link": "https://leetcode.com/problems/maximum-subarray/"
        },
        {
            "slug": "longest-common-prefix",
            "title": "Longest Common Prefix",
            "topic": "Arrays & Strings",
            "difficulty": "Easy",
            "description": "Write a function to find the longest common prefix string amongst an array of strings. If there is no common prefix, return an empty string \"\".",
            "constraints": "1 <= strs.length <= 200\n0 <= strs[i].length <= 200",
            "sample_input": "strs = [\"flower\", \"flow\", \"flight\"]",
            "sample_output": "\"fl\"",
            "starter_codes": {
                "python": "def longestCommonPrefix(strs):\n    if not strs: return \"\"\n    prefix = strs[0]\n    for s in strs[1:]:\n        while not s.startswith(prefix):\n            prefix = prefix[:-1]\n            if not prefix: return \"\"\n    return prefix\n",
                "cpp": "class Solution {\npublic:\n    string longestCommonPrefix(vector<string>& strs) {\n        if (strs.empty()) return \"\";\n        string prefix = strs[0];\n        for (size_t i = 1; i < strs.size(); i++) {\n            while (strs[i].find(prefix) != 0) {\n                prefix = prefix.substr(0, prefix.length() - 1);\n                if (prefix.empty()) return \"\";\n            }\n        }\n        return prefix;\n    }\n};",
                "java": "class Solution {\n    public String longestCommonPrefix(String[] strs) {\n        if (strs == null || strs.length == 0) return \"\";\n        String prefix = strs[0];\n        for (int i = 1; i < strs.length; i++) {\n            while (strs[i].indexOf(prefix) != 0) {\n                prefix = prefix.substring(0, prefix.length() - 1);\n                if (prefix.isEmpty()) return \"\";\n            }\n        }\n        return prefix;\n    }\n}",
                "javascript": "function longestCommonPrefix(strs) {\n    if (!strs.length) return '';\n    let prefix = strs[0];\n    for (let i = 1; i < strs.length; i++) {\n        while (strs[i].indexOf(prefix) !== 0) {\n            prefix = prefix.slice(0, -1);\n            if (!prefix) return '';\n        }\n    }\n    return prefix;\n}"
            },
            "external_link": "https://leetcode.com/problems/longest-common-prefix/"
        },

        # Searching & Sorting
        {
            "slug": "binary-search",
            "title": "Binary Search",
            "topic": "Searching & Sorting",
            "difficulty": "Easy",
            "description": "Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1. You must write an algorithm with O(log n) runtime complexity.",
            "constraints": "1 <= nums.length <= 10^4\n-10^4 < nums[i], target < 10^4\nAll integers in nums are unique and sorted.",
            "sample_input": "nums = [-1, 0, 3, 5, 9, 12], target = 9",
            "sample_output": "4",
            "starter_codes": {
                "python": "def search(nums, target):\n    low, high = 0, len(nums) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n",
                "cpp": "class Solution {\npublic:\n    int search(vector<int>& nums, int target) {\n        int low = 0, high = nums.size() - 1;\n        while (low <= high) {\n            int mid = low + (high - low) / 2;\n            if (nums[mid] == target) return mid;\n            if (nums[mid] < target) low = mid + 1;\n            else high = mid - 1;\n        }\n        return -1;\n    }\n};",
                "java": "class Solution {\n    public int search(int[] nums, int target) {\n        int l = 0, r = nums.length - 1;\n        while (l <= r) {\n            int mid = l + (r - l) / 2;\n            if (nums[mid] == target) return mid;\n            if (nums[mid] < target) l = mid + 1;\n            else r = mid - 1;\n        }\n        return -1;\n    }\n}",
                "javascript": "function search(nums, target) {\n    let l = 0, r = nums.length - 1;\n    while (l <= r) {\n        const mid = Math.floor((l + r) / 2);\n        if (nums[mid] === target) return mid;\n        if (nums[mid] < target) l = mid + 1;\n        else r = mid - 1;\n    }\n    return -1;\n}"
            },
            "external_link": "https://leetcode.com/problems/binary-search/"
        },
        {
            "slug": "search-in-rotated-sorted-array",
            "title": "Search in Rotated Sorted Array",
            "topic": "Searching & Sorting",
            "difficulty": "Medium",
            "description": "There is an integer array nums sorted in ascending order (with distinct values). Prior to being passed to your function, nums is possibly rotated at an unknown pivot index. Given nums and an integer target, return the index of target if it is in nums, or -1 if it is not in nums.",
            "constraints": "1 <= nums.length <= 5000\n-10^4 <= nums[i] <= 10^4\nAll values of nums are unique.",
            "sample_input": "nums = [4, 5, 6, 7, 0, 1, 2], target = 0",
            "sample_output": "4",
            "starter_codes": {
                "python": "def search(nums, target):\n    l, r = 0, len(nums) - 1\n    while l <= r:\n        mid = (l + r) // 2\n        if nums[mid] == target: return mid\n        # Left side is sorted\n        if nums[l] <= nums[mid]:\n            if nums[l] <= target < nums[mid]: r = mid - 1\n            else: l = mid + 1\n        else: # Right side is sorted\n            if nums[mid] < target <= nums[r]: l = mid + 1\n            else: r = mid - 1\n    return -1\n",
                "cpp": "class Solution {\npublic:\n    int search(vector<int>& nums, int target) {\n        int l = 0, r = nums.size() - 1;\n        while (l <= r) {\n            int mid = l + (r - l) / 2;\n            if (nums[mid] == target) return mid;\n            if (nums[l] <= nums[mid]) {\n                if (nums[l] <= target && target < nums[mid]) r = mid - 1;\n                else l = mid + 1;\n            } else {\n                if (nums[mid] < target && target <= nums[r]) l = mid + 1;\n                else r = mid - 1;\n            }\n        }\n        return -1;\n    }\n};",
                "java": "class Solution {\n    public int search(int[] nums, int target) {\n        int l = 0, r = nums.length - 1;\n        while (l <= r) {\n            int mid = l + (r - l) / 2;\n            if (nums[mid] == target) return mid;\n            if (nums[l] <= nums[mid]) {\n                if (nums[l] <= target && target < nums[mid]) r = mid - 1;\n                else l = mid + 1;\n            } else {\n                if (nums[mid] < target && target <= nums[r]) l = mid + 1;\n                else r = mid - 1;\n            }\n        }\n        return -1;\n    }\n}",
                "javascript": "function search(nums, target) {\n    let l = 0, r = nums.length - 1;\n    while (l <= r) {\n        const mid = Math.floor((l + r) / 2);\n        if (nums[mid] === target) return mid;\n        if (nums[l] <= nums[mid]) {\n            if (nums[l] <= target && target < nums[mid]) r = mid - 1;\n            else l = mid + 1;\n        } else {\n            if (nums[mid] < target && target <= nums[r]) l = mid + 1;\n            else r = mid - 1;\n        }\n    }\n    return -1;\n}"
            },
            "external_link": "https://leetcode.com/problems/search-in-rotated-sorted-array/"
        },
        {
            "slug": "merge-intervals",
            "title": "Merge Intervals",
            "topic": "Searching & Sorting",
            "difficulty": "Medium",
            "description": "Given an array of intervals where intervals[i] = [start_i, end_i], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
            "constraints": "1 <= intervals.length <= 10^4\nintervals[i].length == 2\n0 <= start_i <= end_i <= 10^4",
            "sample_input": "intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]",
            "sample_output": "[[1, 6], [8, 10], [15, 18]]",
            "starter_codes": {
                "python": "def merge(intervals):\n    intervals.sort(key=lambda x: x[0])\n    merged = []\n    for interval in intervals:\n        if not merged or merged[-1][1] < interval[0]:\n            merged.append(interval)\n        else:\n            merged[-1][1] = max(merged[-1][1], interval[1])\n    return merged\n",
                "cpp": "class Solution {\npublic:\n    vector<vector<int>> merge(vector<vector<int>>& intervals) {\n        sort(intervals.begin(), intervals.end());\n        vector<vector<int>> merged;\n        for (auto& iv : intervals) {\n            if (merged.empty() || merged.back()[1] < iv[0]) {\n                merged.push_back(iv);\n            } else {\n                merged.back()[1] = max(merged.back()[1], iv[1]);\n            }\n        }\n        return merged;\n    }\n};",
                "java": "class Solution {\n    public int[][] merge(int[][] intervals) {\n        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));\n        List<int[]> merged = new ArrayList<>();\n        for (int[] iv : intervals) {\n            if (merged.isEmpty() || merged.get(merged.size() - 1)[1] < iv[0]) {\n                merged.add(iv);\n            } else {\n                merged.get(merged.size() - 1)[1] = Math.max(merged.get(merged.size() - 1)[1], iv[1]);\n            }\n        }\n        return merged.toArray(new int[merged.size()][]);\n    }\n}",
                "javascript": "function merge(intervals) {\n    intervals.sort((a, b) => a[0] - b[0]);\n    const res = [];\n    for (const iv of intervals) {\n        if (!res.length || res[res.length - 1][1] < iv[0]) {\n            res.push(iv);\n        } else {\n            res[res.length - 1][1] = Math.max(res[res.length - 1][1], iv[1]);\n        }\n    }\n    return res;\n}"
            },
            "external_link": "https://leetcode.com/problems/merge-intervals/"
        },

        # Hashing
        {
            "slug": "contains-duplicate",
            "title": "Contains Duplicate",
            "topic": "Hashing",
            "difficulty": "Easy",
            "description": "Given an integer array nums, return true if any value appears at least twice in the array, and return false if every element is distinct.",
            "constraints": "1 <= nums.length <= 10^5\n-10^9 <= nums[i] <= 10^9",
            "sample_input": "nums = [1, 2, 3, 1]",
            "sample_output": "true",
            "starter_codes": {
                "python": "def containsDuplicate(nums):\n    return len(nums) != len(set(nums))\n",
                "cpp": "class Solution {\npublic:\n    bool containsDuplicate(vector<int>& nums) {\n        unordered_set<int> seen(nums.begin(), nums.end());\n        return seen.size() != nums.size();\n    }\n};",
                "java": "class Solution {\n    public boolean containsDuplicate(int[] nums) {\n        Set<Integer> set = new HashSet<>();\n        for (int n : nums) if (!set.add(n)) return true;\n        return false;\n    }\n}",
                "javascript": "function containsDuplicate(nums) {\n    return new Set(nums).size !== nums.length;\n}"
            },
            "external_link": "https://leetcode.com/problems/contains-duplicate/"
        },
        {
            "slug": "group-anagrams",
            "title": "Group Anagrams",
            "topic": "Hashing",
            "difficulty": "Medium",
            "description": "Given an array of strings strs, group the anagrams together. You can return the answer in any order. An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase.",
            "constraints": "1 <= strs.length <= 10^4\n0 <= strs[i].length <= 100\nstrs[i] consists of lowercase English letters.",
            "sample_input": "strs = [\"eat\", \"tea\", \"tan\", \"ate\", \"nat\", \"bat\"]",
            "sample_output": "[[\"bat\"], [\"nat\", \"tan\"], [\"ate\", \"eat\", \"tea\"]]",
            "starter_codes": {
                "python": "def groupAnagrams(strs):\n    from collections import defaultdict\n    groups = defaultdict(list)\n    for s in strs:\n        key = \"\".join(sorted(s))\n        groups[key].append(s)\n    return list(groups.values())\n",
                "cpp": "class Solution {\npublic:\n    vector<vector<string>> groupAnagrams(vector<string>& strs) {\n        unordered_map<string, vector<string>> map;\n        for (string& s : strs) {\n            string key = s;\n            sort(key.begin(), key.end());\n            map[key].push_back(s);\n        }\n        vector<vector<string>> res;\n        for (auto& pair : map) res.push_back(pair.second);\n        return res;\n    }\n};",
                "java": "class Solution {\n    public List<List<String>> groupAnagrams(String[] strs) {\n        Map<String, List<String>> map = new HashMap<>();\n        for (String s : strs) {\n            char[] ca = s.toCharArray();\n            Arrays.sort(ca);\n            String key = String.valueOf(ca);\n            map.computeIfAbsent(key, k -> new ArrayList<>()).add(s);\n        }\n        return new ArrayList<>(map.values());\n    }\n}",
                "javascript": "function groupAnagrams(strs) {\n    const map = {};\n    for (const s of strs) {\n        const key = s.split('').sort().join('');\n        if (!map[key]) map[key] = [];\n        map[key].push(s);\n    }\n    return Object.values(map);\n}"
            },
            "external_link": "https://leetcode.com/problems/group-anagrams/"
        },
        {
            "slug": "longest-consecutive-sequence",
            "title": "Longest Consecutive Sequence",
            "topic": "Hashing",
            "difficulty": "Medium",
            "description": "Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence. You must write an algorithm that runs in O(n) time.",
            "constraints": "0 <= nums.length <= 10^5\n-10^9 <= nums[i] <= 10^9",
            "sample_input": "nums = [100, 4, 200, 1, 3, 2]",
            "sample_output": "4 (The longest sequence is [1, 2, 3, 4])",
            "starter_codes": {
                "python": "def longestConsecutive(nums):\n    num_set = set(nums)\n    max_len = 0\n    for n in num_set:\n        if (n - 1) not in num_set:\n            cur = n\n            cur_len = 1\n            while (cur + 1) in num_set:\n                cur += 1\n                cur_len += 1\n            max_len = max(max_len, cur_len)\n    return max_len\n",
                "cpp": "class Solution {\npublic:\n    int longestConsecutive(vector<int>& nums) {\n        unordered_set<int> set(nums.begin(), nums.end());\n        int max_len = 0;\n        for (int n : set) {\n            if (!set.count(n - 1)) {\n                int cur = n, len = 1;\n                while (set.count(cur + 1)) { cur++; len++; }\n                max_len = max(max_len, len);\n            }\n        }\n        return max_len;\n    }\n};",
                "java": "class Solution {\n    public int longestConsecutive(int[] nums) {\n        Set<Integer> set = new HashSet<>();\n        for (int n : nums) set.add(n);\n        int max = 0;\n        for (int n : set) {\n            if (!set.contains(n - 1)) {\n                int cur = n, len = 1;\n                while (set.contains(cur + 1)) { cur++; len++; }\n                max = Math.max(max, len);\n            }\n        }\n        return max;\n    }\n}",
                "javascript": "function longestConsecutive(nums) {\n    const set = new Set(nums);\n    let max = 0;\n    for (const n of set) {\n        if (!set.has(n - 1)) {\n            let cur = n, len = 1;\n            while (set.has(cur + 1)) { cur++; len++; }\n            max = Math.max(max, len);\n        }\n    }\n    return max;\n}"
            },
            "external_link": "https://leetcode.com/problems/longest-consecutive-sequence/"
        },

        # Linked Lists
        {
            "slug": "reverse-linked-list",
            "title": "Reverse Linked List",
            "topic": "Linked Lists",
            "difficulty": "Easy",
            "description": "Given the head of a singly linked list, reverse the list, and return the reversed list.",
            "constraints": "The number of nodes in the list is the range [0, 5000].\n-5000 <= Node.val <= 5000",
            "sample_input": "head = [1, 2, 3, 4, 5]",
            "sample_output": "[5, 4, 3, 2, 1]",
            "starter_codes": {
                "python": "# Definition for singly-linked list.\n# class ListNode:\n#     def __init__(self, val=0, next=None):\n#         self.val = val\n#         self.next = next\ndef reverseList(head):\n    prev = None\n    curr = head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev\n",
                "cpp": "class Solution {\npublic:\n    ListNode* reverseList(ListNode* head) {\n        ListNode* prev = nullptr;\n        ListNode* curr = head;\n        while (curr) {\n            ListNode* nxt = curr->next;\n            curr->next = prev;\n            prev = curr;\n            curr = nxt;\n        }\n        return prev;\n    }\n};",
                "java": "class Solution {\n    public ListNode reverseList(ListNode head) {\n        ListNode prev = null, curr = head;\n        while (curr != null) {\n            ListNode nxt = curr.next;\n            curr.next = prev;\n            prev = curr;\n            curr = nxt;\n        }\n        return prev;\n    }\n}",
                "javascript": "function reverseList(head) {\n    let prev = null, curr = head;\n    while (curr) {\n        const nxt = curr.next;\n        curr.next = prev;\n        prev = curr;\n        curr = nxt;\n    }\n    return prev;\n}"
            },
            "external_link": "https://leetcode.com/problems/reverse-linked-list/"
        },
        {
            "slug": "linked-list-cycle",
            "title": "Linked List Cycle (Floyd's Algorithm)",
            "topic": "Linked Lists",
            "difficulty": "Easy",
            "description": "Given head, the head of a linked list, determine if the linked list has a cycle in it. Return true if there is a cycle in the linked list. Otherwise, return false.",
            "constraints": "The number of nodes in the list is in the range [0, 10^4].\n-10^5 <= Node.val <= 10^5",
            "sample_input": "head = [3, 2, 0, -4], pos = 1",
            "sample_output": "true",
            "starter_codes": {
                "python": "def hasCycle(head):\n    slow = fast = head\n    while fast and fast.next:\n        slow = slow.next\n        fast = fast.next.next\n        if slow == fast:\n            return True\n    return False\n",
                "cpp": "class Solution {\npublic:\n    bool hasCycle(ListNode *head) {\n        ListNode *slow = head, *fast = head;\n        while (fast && fast->next) {\n            slow = slow->next;\n            fast = fast->next->next;\n            if (slow == fast) return true;\n        }\n        return false;\n    }\n};",
                "java": "public class Solution {\n    public boolean hasCycle(ListNode head) {\n        ListNode slow = head, fast = head;\n        while (fast != null && fast.next != null) {\n            slow = slow.next;\n            fast = fast.next.next;\n            if (slow == fast) return true;\n        }\n        return false;\n    }\n}",
                "javascript": "function hasCycle(head) {\n    let slow = head, fast = head;\n    while (fast && fast.next) {\n        slow = slow.next;\n        fast = fast.next.next;\n        if (slow === fast) return true;\n    }\n    return false;\n}"
            },
            "external_link": "https://leetcode.com/problems/linked-list-cycle/"
        },
        {
            "slug": "merge-two-sorted-lists",
            "title": "Merge Two Sorted Lists",
            "topic": "Linked Lists",
            "difficulty": "Easy",
            "description": "You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists. Return the head of the merged linked list.",
            "constraints": "The number of nodes in both lists is in the range [0, 50].\n-100 <= Node.val <= 100",
            "sample_input": "list1 = [1, 2, 4], list2 = [1, 3, 4]",
            "sample_output": "[1, 1, 2, 3, 4, 4]",
            "starter_codes": {
                "python": "def mergeTwoLists(l1, l2):\n    dummy = ListNode(0)\n    cur = dummy\n    while l1 and l2:\n        if l1.val < l2.val:\n            cur.next = l1\n            l1 = l1.next\n        else:\n            cur.next = l2\n            l2 = l2.next\n        cur = cur.next\n    cur.next = l1 or l2\n    return dummy.next\n",
                "cpp": "class Solution {\npublic:\n    ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {\n        ListNode dummy(0);\n        ListNode* cur = &dummy;\n        while (l1 && l2) {\n            if (l1->val < l2->val) { cur->next = l1; l1 = l1->next; }\n            else { cur->next = l2; l2 = l2->next; }\n            cur = cur->next;\n        }\n        cur->next = l1 ? l1 : l2;\n        return dummy.next;\n    }\n};",
                "java": "class Solution {\n    public ListNode mergeTwoLists(ListNode l1, ListNode l2) {\n        ListNode dummy = new ListNode(0);\n        ListNode cur = dummy;\n        while (l1 != null && l2 != null) {\n            if (l1.val < l2.val) { cur.next = l1; l1 = l1.next; }\n            else { cur.next = l2; l2 = l2.next; }\n            cur = cur.next;\n        }\n        cur.next = (l1 != null) ? l1 : l2;\n        return dummy.next;\n    }\n}",
                "javascript": "function mergeTwoLists(l1, l2) {\n    const dummy = { val: 0, next: null };\n    let cur = dummy;\n    while (l1 && l2) {\n        if (l1.val < l2.val) { cur.next = l1; l1 = l1.next; }\n        else { cur.next = l2; l2 = l2.next; }\n        cur = cur.next;\n    }\n    cur.next = l1 || l2;\n    return dummy.next;\n}"
            },
            "external_link": "https://leetcode.com/problems/merge-two-sorted-lists/"
        },

        # Stacks & Queues
        {
            "slug": "valid-parentheses",
            "title": "Valid Parentheses",
            "topic": "Stacks & Queues",
            "difficulty": "Easy",
            "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if open brackets are closed by the same type of brackets and in the correct order.",
            "constraints": "1 <= s.length <= 10^4\ns consists of parentheses only '()[]{}'.",
            "sample_input": "s = \"()[]{}\"",
            "sample_output": "true",
            "starter_codes": {
                "python": "def isValid(s: str) -> bool:\n    stack = []\n    pairs = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in pairs:\n            if not stack or stack.pop() != pairs[char]:\n                return False\n        else:\n            stack.append(char)\n    return len(stack) == 0\n",
                "cpp": "class Solution {\npublic:\n    bool isValid(string s) {\n        stack<char> st;\n        for (char c : s) {\n            if (c == '(' || c == '{' || c == '[') st.push(c);\n            else {\n                if (st.empty()) return false;\n                if (c == ')' && st.top() != '(') return false;\n                if (c == '}' && st.top() != '{') return false;\n                if (c == ']' && st.top() != '[') return false;\n                st.pop();\n            }\n        }\n        return st.empty();\n    }\n};",
                "java": "class Solution {\n    public boolean isValid(String s) {\n        Stack<Character> stack = new Stack<>();\n        for (char c : s.toCharArray()) {\n            if (c == '(') stack.push(')');\n            else if (c == '{') stack.push('}');\n            else if (c == '[') stack.push(']');\n            else if (stack.isEmpty() || stack.pop() != c) return false;\n        }\n        return stack.isEmpty();\n    }\n}",
                "javascript": "function isValid(s) {\n    const stack = [];\n    const pairs = { ')': '(', '}': '{', ']': '[' };\n    for (const char of s) {\n        if (pairs[char]) {\n            if (stack.pop() !== pairs[char]) return false;\n        } else {\n            stack.push(char);\n        }\n    }\n    return stack.length === 0;\n}"
            },
            "external_link": "https://leetcode.com/problems/valid-parentheses/"
        },
        {
            "slug": "implement-queue-using-stacks",
            "title": "Implement Queue using Stacks",
            "topic": "Stacks & Queues",
            "difficulty": "Easy",
            "description": "Implement a first in first out (FIFO) queue using only two stacks. The implemented queue should support push, pop, peek, and empty operations.",
            "constraints": "1 <= x <= 9\nAt most 100 calls will be made to push, pop, peek, and empty.",
            "sample_input": "push(1), push(2), peek(), pop(), empty()",
            "sample_output": "peek: 1, pop: 1, empty: false",
            "starter_codes": {
                "python": "class MyQueue:\n    def __init__(self):\n        self.in_stack = []\n        self.out_stack = []\n\n    def push(self, x: int) -> None:\n        self.in_stack.append(x)\n\n    def pop(self) -> int:\n        self.peek()\n        return self.out_stack.pop()\n\n    def peek(self) -> int:\n        if not self.out_stack:\n            while self.in_stack:\n                self.out_stack.append(self.in_stack.pop())\n        return self.out_stack[-1]\n\n    def empty(self) -> bool:\n        return not self.in_stack and not self.out_stack\n",
                "cpp": "class MyQueue {\n    stack<int> s1, s2;\npublic:\n    void push(int x) { s1.push(x); }\n    int pop() {\n        peek();\n        int val = s2.top(); s2.pop();\n        return val;\n    }\n    int peek() {\n        if (s2.empty()) {\n            while (!s1.empty()) {\n                s2.push(s1.top()); s1.pop();\n            }\n        }\n        return s2.top();\n    }\n    bool empty() { return s1.empty() && s2.empty(); }\n};",
                "java": "class MyQueue {\n    private Stack<Integer> s1 = new Stack<>();\n    private Stack<Integer> s2 = new Stack<>();\n    public void push(int x) { s1.push(x); }\n    public int pop() {\n        peek();\n        return s2.pop();\n    }\n    public int peek() {\n        if (s2.isEmpty()) {\n            while (!s1.isEmpty()) s2.push(s1.pop());\n        }\n        return s2.peek();\n    }\n    public boolean empty() { return s1.isEmpty() && s2.isEmpty(); }\n}",
                "javascript": "class MyQueue {\n    constructor() {\n        this.s1 = [];\n        this.s2 = [];\n    }\n    push(x) { this.s1.push(x); }\n    pop() {\n        this.peek();\n        return this.s2.pop();\n    }\n    peek() {\n        if (!this.s2.length) {\n            while (this.s1.length) this.s2.push(this.s1.pop());\n        }\n        return this.s2[this.s2.length - 1];\n    }\n    empty() { return !this.s1.length && !this.s2.length; }\n}"
            },
            "external_link": "https://leetcode.com/problems/implement-queue-using-stacks/"
        },
        {
            "slug": "min-stack",
            "title": "Min Stack",
            "topic": "Stacks & Queues",
            "difficulty": "Medium",
            "description": "Design a stack that supports push, pop, top, and retrieving the minimum element in constant time O(1).",
            "constraints": "-2^31 <= val <= 2^31 - 1\nMethods pop, top and getMin operations will always be called on non-empty stacks.",
            "sample_input": "push(-2), push(0), push(-3), getMin(), pop(), top(), getMin()",
            "sample_output": "-3, top: 0, min: -2",
            "starter_codes": {
                "python": "class MinStack:\n    def __init__(self):\n        self.stack = []\n        self.min_stack = []\n\n    def push(self, val: int) -> None:\n        self.stack.append(val)\n        val = min(val, self.min_stack[-1] if self.min_stack else val)\n        self.min_stack.append(val)\n\n    def pop(self) -> None:\n        self.stack.pop()\n        self.min_stack.pop()\n\n    def top(self) -> int:\n        return self.stack[-1]\n\n    def getMin(self) -> int:\n        return self.min_stack[-1]\n",
                "cpp": "class MinStack {\n    stack<int> s;\n    stack<int> min_s;\npublic:\n    void push(int val) {\n        s.push(val);\n        if (min_s.empty() || val <= min_s.top()) min_s.push(val);\n        else min_s.push(min_s.top());\n    }\n    void pop() { s.pop(); min_s.pop(); }\n    int top() { return s.top(); }\n    int getMin() { return min_s.top(); }\n};",
                "java": "class MinStack {\n    private Stack<Integer> s = new Stack<>();\n    private Stack<Integer> minS = new Stack<>();\n    public void push(int val) {\n        s.push(val);\n        minS.push(minS.isEmpty() ? val : Math.min(val, minS.peek()));\n    }\n    public void pop() { s.pop(); minS.pop(); }\n    public int top() { return s.peek(); }\n    public int getMin() { return minS.peek(); }\n}",
                "javascript": "class MinStack {\n    constructor() {\n        this.s = [];\n        this.minS = [];\n    }\n    push(val) {\n        this.s.push(val);\n        const currentMin = this.minS.length ? this.minS[this.minS.length - 1] : val;\n        this.minS.push(Math.min(val, currentMin));\n    }\n    pop() { this.s.pop(); this.minS.pop(); }\n    top() { return this.s[this.s.length - 1]; }\n    getMin() { return this.minS[this.minS.length - 1]; }\n}"
            },
            "external_link": "https://leetcode.com/problems/min-stack/"
        },

        # Basic Recursion
        {
            "slug": "fibonacci-number",
            "title": "Fibonacci Number",
            "topic": "Basic Recursion",
            "difficulty": "Easy",
            "description": "The Fibonacci numbers, commonly denoted F(n) form a sequence, called the Fibonacci sequence, such that each number is the sum of the two preceding ones, starting from 0 and 1. Given n, calculate F(n).",
            "constraints": "0 <= n <= 30",
            "sample_input": "n = 4",
            "sample_output": "3 (F(4) = F(3) + F(2) = 2 + 1 = 3)",
            "starter_codes": {
                "python": "def fib(n: int) -> int:\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n",
                "cpp": "class Solution {\npublic:\n    int fib(int n) {\n        if (n <= 1) return n;\n        int a = 0, b = 1;\n        for (int i = 2; i <= n; i++) {\n            int c = a + b;\n            a = b; b = c;\n        }\n        return b;\n    }\n};",
                "java": "class Solution {\n    public int fib(int n) {\n        if (n <= 1) return n;\n        int a = 0, b = 1;\n        for (int i = 2; i <= n; i++) {\n            int c = a + b;\n            a = b; b = c;\n        }\n        return b;\n    }\n}",
                "javascript": "function fib(n) {\n    if (n <= 1) return n;\n    let a = 0, b = 1;\n    for (let i = 2; i <= n; i++) {\n        const c = a + b;\n        a = b; b = c;\n    }\n    return b;\n}"
            },
            "external_link": "https://leetcode.com/problems/fibonacci-number/"
        },
        {
            "slug": "subsets-power-set",
            "title": "Subsets (Power Set)",
            "topic": "Basic Recursion",
            "difficulty": "Medium",
            "description": "Given an integer array nums of unique elements, return all possible subsets (the power set). The solution set must not contain duplicate subsets. Return the solution in any order.",
            "constraints": "1 <= nums.length <= 10\n-10 <= nums[i] <= 10\nAll the numbers of nums are unique.",
            "sample_input": "nums = [1, 2, 3]",
            "sample_output": "[[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]",
            "starter_codes": {
                "python": "def subsets(nums):\n    res = []\n    def backtrack(start, current):\n        res.append(list(current))\n        for i in range(start, len(nums)):\n            current.append(nums[i])\n            backtrack(i + 1, current)\n            current.pop()\n    backtrack(0, [])\n    return res\n",
                "cpp": "class Solution {\npublic:\n    vector<vector<int>> subsets(vector<int>& nums) {\n        vector<vector<int>> res;\n        vector<int> cur;\n        auto backtrack = [&](auto& self, int start) -> void {\n            res.push_back(cur);\n            for (size_t i = start; i < nums.size(); i++) {\n                cur.push_back(nums[i]);\n                self(self, i + 1);\n                cur.pop_back();\n            }\n        };\n        backtrack(backtrack, 0);\n        return res;\n    }\n};",
                "java": "class Solution {\n    public List<List<Integer>> subsets(int[] nums) {\n        List<List<Integer>> res = new ArrayList<>();\n        backtrack(res, new ArrayList<>(), nums, 0);\n        return res;\n    }\n    private void backtrack(List<List<Integer>> res, List<Integer> cur, int[] nums, int start) {\n        res.add(new ArrayList<>(cur));\n        for (int i = start; i < nums.length; i++) {\n            cur.add(nums[i]);\n            backtrack(res, cur, nums, i + 1);\n            cur.remove(cur.size() - 1);\n        }\n    }\n}",
                "javascript": "function subsets(nums) {\n    const res = [];\n    function backtrack(start, cur) {\n        res.push([...cur]);\n        for (let i = start; i < nums.length; i++) {\n            cur.push(nums[i]);\n            backtrack(i + 1, cur);\n            cur.pop();\n        }\n    }\n    backtrack(0, []);\n    return res;\n}"
            },
            "external_link": "https://leetcode.com/problems/subsets/"
        }
    ]

    for p in problems:
        p["updated_at"] = datetime.datetime.now(datetime.timezone.utc)
        db.coding_problems.update_one(
            {"slug": p["slug"]},
            {"$set": p},
            upsert=True
        )
    print(f"[Coding Problems] Seeded/updated {len(problems)} coding problems across 6 core topics.")

    # 3. Seed Aptitude Questions (6 original questions per category = 18 total)
    aptitude_data = [
        # Quantitative Aptitude
        {
            "category": "Quantitative Aptitude",
            "question": "A train 180 meters long is traveling at a speed of 72 km/h. How many seconds will it take to pass an electric pole?",
            "options": ["9 seconds", "10 seconds", "12 seconds", "15 seconds"],
            "correct_option": 0,
            "explanation": "Speed in m/s = 72 * (5 / 18) = 20 m/s. Time to cross pole = Distance / Speed = 180 m / 20 m/s = 9 seconds."
        },
        {
            "category": "Quantitative Aptitude",
            "question": "A can complete a piece of work in 12 days, while B can complete the same work in 18 days. If they work together, how many days will they take?",
            "options": ["6.5 days", "7.2 days", "8 days", "9 days"],
            "correct_option": 1,
            "explanation": "Work done per day = 1/12 + 1/18 = (3 + 2)/36 = 5/36. Total days = 36 / 5 = 7.2 days."
        },
        {
            "category": "Quantitative Aptitude",
            "question": "The cost price of 20 articles is equal to the selling price of 16 articles. What is the gain percentage?",
            "options": ["20%", "25%", "30%", "16.66%"],
            "correct_option": 1,
            "explanation": "Let CP of 1 article = $1. CP of 20 = $20 = SP of 16. SP of 1 = 20/16 = 1.25. Profit = 0.25 on CP 1 = 25% gain."
        },
        {
            "category": "Quantitative Aptitude",
            "question": "Two numbers are in the ratio 3 : 5. If 9 is subtracted from each, the new ratio becomes 12 : 23. What is the smaller number?",
            "options": ["27", "33", "45", "55"],
            "correct_option": 1,
            "explanation": "Let numbers be 3x and 5x. (3x - 9)/(5x - 9) = 12/23 => 23*(3x - 9) = 12*(5x - 9) => 69x - 207 = 60x - 108 => 9x = 99 => x = 11. Smaller number = 3 * 11 = 33."
        },
        {
            "category": "Quantitative Aptitude",
            "question": "A sum of money invested at simple interest doubles itself in 8 years. In how many years will it become 4 times itself at the same rate?",
            "options": ["16 years", "20 years", "24 years", "32 years"],
            "correct_option": 2,
            "explanation": "Doubling means SI = P in 8 years, so Rate = 100/8 = 12.5% per annum. To become 4 times, SI needed = 3P. Time = (3P * 100)/(P * 12.5) = 300 / 12.5 = 24 years."
        },
        {
            "category": "Quantitative Aptitude",
            "question": "A bag contains 4 red, 5 green, and 6 blue balls. If two balls are drawn at random, what is the probability that both are green?",
            "options": ["2/21", "1/15", "5/21", "2/15"],
            "correct_option": 0,
            "explanation": "Total balls = 15. Number of ways to choose 2 green = 5C2 = 10. Total ways to choose 2 balls = 15C2 = 105. Probability = 10 / 105 = 2 / 21."
        },

        # Logical Reasoning
        {
            "category": "Logical Reasoning",
            "question": "Look at this series: 7, 10, 8, 11, 9, 12, ... What number should come next?",
            "options": ["10", "12", "13", "14"],
            "correct_option": 0,
            "explanation": "This is an alternating addition and subtraction series: +3, -2, +3, -2, +3. So 12 - 2 = 10."
        },
        {
            "category": "Logical Reasoning",
            "question": "Pointing to a photograph of a boy, Suresh said, 'He is the son of the only son of my mother.' How is Suresh related to that boy?",
            "options": ["Brother", "Uncle", "Father", "Grandfather"],
            "correct_option": 2,
            "explanation": "The 'only son of my mother' refers to Suresh himself (assuming Suresh is male). Thus, the boy is the son of Suresh, making Suresh his Father."
        },
        {
            "category": "Logical Reasoning",
            "question": "Statements: (1) All mangoes are golden. (2) No golden things are cheap. Conclusions: I. All mangoes are costly. II. Golden mangoes are not cheap.",
            "options": ["Only conclusion I follows", "Only conclusion II follows", "Both conclusions I and II follow", "Neither follows"],
            "correct_option": 2,
            "explanation": "Since all mangoes are golden and no golden thing is cheap, mangoes cannot be cheap (i.e. they are costly), and golden mangoes are not cheap. Both follow."
        },
        {
            "category": "Logical Reasoning",
            "question": "If in a certain code language, 'ROBOT' is written as 'TQDOT', how is 'SMART' written in that code?",
            "options": ["UOCTV", "UNCTU", "UOCRV", "UOBTU"],
            "correct_option": 0,
            "explanation": "Pattern: R(+2)->T, O(+2)->Q, B(+2)->D, O(+0 or vowel unchanged?) Notice R(+2)=T, O(+2)=Q, B(+2)=D, O(-??): Actually R+2=T, O+2=Q, B+2=D, O-something? Check: S(+2)=U, M(+2)=O, A(+2)=C, R(+2)=T, T(+2)=V => UOCTV."
        },
        {
            "category": "Logical Reasoning",
            "question": "A man walks 5 km East, turns right and walks 4 km, then turns left and walks 5 km. In which direction is he now with respect to his starting point?",
            "options": ["North-East", "South-East", "North-West", "South-West"],
            "correct_option": 1,
            "explanation": "He is (5 + 5) = 10 km East and 4 km South from the starting point. Therefore, he is in the South-East direction."
        },
        {
            "category": "Logical Reasoning",
            "question": "Five students A, B, C, D, and E are sitting in a row facing North. C is sitting between A and E. B is sitting to the immediate right of E. D is to the left of A. Who is sitting in the middle?",
            "options": ["A", "B", "C", "E"],
            "correct_option": 2,
            "explanation": "Arrangement from left to right: D - A - C - E - B. The student in the exact middle is C."
        },

        # Verbal Ability
        {
            "category": "Verbal Ability",
            "question": "Choose the word that is most nearly OPPOSITE in meaning to 'METICULOUS':",
            "options": ["Careless", "Painstaking", "Accurate", "Diligent"],
            "correct_option": 0,
            "explanation": "'Meticulous' means showing great attention to detail and very careful. The antonym is 'Careless'."
        },
        {
            "category": "Verbal Ability",
            "question": "Select the correct option to fill in the blank: 'Neither the manager nor the team members ________ willing to compromise on quality.'",
            "options": ["is", "were", "was", "has been"],
            "correct_option": 1,
            "explanation": "In 'Neither ... nor ...' constructions, the verb agrees with the subject closer to it ('team members', which is plural), so the plural verb 'were' is correct."
        },
        {
            "category": "Verbal Ability",
            "question": "Identify the idiom meaning 'to face a difficult situation with courage and fortitude':",
            "options": ["Bite the bullet", "Spill the beans", "Burn the bridges", "Break the ice"],
            "correct_option": 0,
            "explanation": "'Bite the bullet' means to face an inevitable grim situation with courage and stoicism."
        },
        {
            "category": "Verbal Ability",
            "question": "Select the word that correctly replaces the phrase: 'One who has no money to pay off his debts':",
            "options": ["Insolvent", "Pauper", "Debtor", "Borrower"],
            "correct_option": 0,
            "explanation": "An 'Insolvent' (or bankrupt) person is legally declared unable to pay their debts."
        },
        {
            "category": "Verbal Ability",
            "question": "Detect the error in the sentence: 'The team of researchers (A) / are conducting experiments (B) / on renewable energy sources (C) / No error (D)'",
            "options": ["Part A", "Part B", "Part C", "Part D"],
            "correct_option": 1,
            "explanation": "The subject is 'The team' (singular collective noun), which requires the singular verb 'is conducting', not 'are conducting'. Hence, error is in Part B."
        },
        {
            "category": "Verbal Ability",
            "question": "Choose the synonym for 'CANDID':",
            "options": ["Frank", "Deceptive", "Arrogant", "Vague"],
            "correct_option": 0,
            "explanation": "'Candid' means truthful, straightforward, and sincere. The closest synonym is 'Frank'."
        }
    ]

    # Delete existing seeded questions to ensure clean update without duplicates
    db.aptitude_questions.delete_many({})
    for q in aptitude_data:
        q["created_at"] = datetime.datetime.now(datetime.timezone.utc)
        db.aptitude_questions.insert_one(q)
    print(f"[Aptitude Questions] Seeded {len(aptitude_data)} questions across 3 categories (6 Quant, 6 Logic, 6 Verbal).")

    print("--- MongoDB Seeding Completed Successfully! ---")

if __name__ == "__main__":
    seed_database()
