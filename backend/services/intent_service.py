import os
import requests
import json
import re
from dotenv import load_dotenv
import openai
from typing import List, Dict, Any

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

ENHANCED_SYSTEM_PROMPT = """
You are a multi-intent task management assistant. You can handle multiple operations in a single request.

CRITICAL RULES:
1. Output ONLY valid JSON - no markdown, no explanations
2. A single user message can contain multiple intents (create, update, delete)
3. Each intent must be processed separately in the order mentioned
4. For complex multi-task operations, use the "multi_intent" format
5. EXTRACT TASK NUMBERS when mentioned (e.g., "task 1", "task number 3", "tasks 5 and 7")
6. Support "complete all tasks" and "complete all tasks for today" operations

OUTPUT FORMATS:

1. SINGLE INTENT (simple operations):
{
  "intent": "create_task|update_task|delete_task|list_tasks|small_talk",
  "task": "task title",
  "due_date": "today|tomorrow|this_week|next_week|YYYY-MM-DD",
  "assignee": "person name",
  "action": "complete|reopen|update_title|complete_all|complete_today",
  "new_title": "updated title if applicable",
  "task_numbers": [1, 2, 3]  // for specific task number operations
}

2. MULTI-INTENT (mixed operations in one request):
{
  "intent": "multi_intent",
  "operations": [
    {
      "intent": "create_task",
      "tasks": [
        {"title": "Task 1", "due_date": "today", "assignee": "John"},
        {"title": "Task 2", "due_date": "tomorrow", "assignee": "Jane"}
      ]
    },
    {
      "intent": "update_task",
      "action": "complete",
      "task_numbers": [1, 3, 5],  // Specific task numbers
      "filter": {"all": true}  // For "complete all"
    }
  ]
}

3. BATCH OPERATIONS:
{
  "intent": "delete_task",
  "filter": {"all": true}  // Delete all tasks
}

OR

{
  "intent": "update_task",
  "action": "complete_today",
  "filter": {"today": true}  // Complete tasks for today
}

4. TASK NUMBER OPERATIONS:
{
  "intent": "update_task",
  "action": "complete",
  "task_numbers": [1, 2, 3]  // Update specific task numbers
}

OR

{
  "intent": "delete_task",
  "task_numbers": [4, 5]  // Delete specific task numbers
}

EXAMPLES:

Input: "Complete task 1 and task 3"
Output: {
  "intent": "update_task",
  "action": "complete",
  "task_numbers": [1, 3]
}

Input: "Delete all tasks"
Output: {
  "intent": "delete_task",
  "filter": {"all": true}
}

Input: "Complete all tasks for today"
Output: {
  "intent": "update_task",
  "action": "complete_today",
  "filter": {"today": true}
}

Input: "Update task 2 to 'Buy groceries' and delete task 5"
Output: {
  "intent": "multi_intent",
  "operations": [
    {
      "intent": "update_task",
      "action": "update_title",
      "task_numbers": [2],
      "new_title": "Buy groceries"
    },
    {
      "intent": "delete_task",
      "task_numbers": [5]
    }
  ]
}

Input: "Mark task number 1 as complete and create a new task for tomorrow"
Output: {
  "intent": "multi_intent",
  "operations": [
    {
      "intent": "update_task",
      "action": "complete",
      "task_numbers": [1]
    },
    {
      "intent": "create_task",
      "tasks": [
        {"title": "new task", "due_date": "tomorrow", "assignee": ""}
      ]
    }
  ]
}

TASK NUMBER EXTRACTION RULES:
- "task 1" → [1]
- "tasks 2, 3 and 4" → [2, 3, 4]
- "task number 5" → [5]
- "tasks number 1 and 3" → [1, 3]
- "complete the first three tasks" → [1, 2, 3]
"""

def extract_task_numbers(text):
    """Extract task numbers from text - SIMPLE AND SAFE"""
    numbers = []
    try:
        matches = re.findall(r'\b\d+\b', text)
        for num_str in matches:
            if num_str.isdigit():
                numbers.append(int(num_str))
    except:
        pass
    return list(set(numbers))


def get_intent(user_text: str) -> dict:
    """Get intent using Mistral with enhanced multi-task support"""
    try:
        task_numbers = extract_task_numbers(user_text)
        
        text_lower = user_text.lower()
        
        if "complete all tasks for today" in text_lower or "mark all today's tasks as complete" in text_lower:
            return {
                "intent": "update_task",
                "action": "complete_today",
                "filter": {"today": True},
                "task_numbers": []
            }
        
        if "complete all tasks" in text_lower or "mark all as complete" in text_lower:
            return {
                "intent": "update_task",
                "action": "complete_all",
                "filter": {"all": True},
                "task_numbers": []
            }
        
        if "delete all tasks" in text_lower or "remove all tasks" in text_lower:
            return {
                "intent": "delete_task",
                "filter": {"all": True},
                "task_numbers": []
            }
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "system", "content": ENHANCED_SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            },
            timeout=60
        )

        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        print("🔍 Enhanced LLM RAW OUTPUT:", raw)
        parsed = json.loads(raw)
        
        if task_numbers and "task_numbers" not in parsed:
            parsed["task_numbers"] = task_numbers
        
        if parsed.get("intent") == "multi_intent":
            return parsed
        else:
            return {
                "intent": parsed.get("intent", "").lower(),
                "task": parsed.get("task", ""),
                "due_date": parsed.get("due_date", ""),
                "assignee": parsed.get("assignee", ""),
                "tasks": parsed.get("tasks", []),
                "action": parsed.get("action", ""),
                "new_title": parsed.get("new_title", ""),
                "task_numbers": parsed.get("task_numbers", task_numbers),
                "filter": parsed.get("filter", {}),
                "operations": []
            }

    except Exception as e:
        print("❌ Enhanced intent error:", e)
        return {
            "intent": "unknown",
            "task": "",
            "due_date": "",
            "tasks": [],
            "action": "",
            "task_numbers": extract_task_numbers(user_text),
            "filter": {},
            "operations": []
        }