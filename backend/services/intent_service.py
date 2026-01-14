import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

SYSTEM_PROMPT = """
You are an intent classification engine.

Rules:
- Output ONLY valid JSON
- No markdown
- No explanations

Supported intents:
- create_task
- delete_task
- list_tasks
- update_task
- small_talk

DELETE TASK RULES:
- Use intent = delete_task
- If user wants to delete ALL tasks, set "tasks" to the string "all"
- If user wants to delete MULTIPLE tasks, use "tasks" as a list of task objects
- If user wants to delete ONE task, use "task" as a string
- Never mix "task" and "tasks"

JSON formats:

SINGLE TASK:
{
  "intent": "",
  "task": "",
  "due_date": ""
}

MULTIPLE TASKS (ONLY when user gives many tasks in one message):
{
  "intent": "create_task",
  "task": "",
  "due_date": "",
  "tasks": [
    {
      "title": "",
      "assignee": "",
      "due_date": ""
    }
  ]
}

MULTIPLE TASK UPDATE (when user updates many tasks):
{
  "intent": "update_task",
  "action": "",
  "tasks": [
    {
      "title": ""
    }
  ]
}

MULTIPLE TASKS:
{
  "intent": "delete_task",
  "tasks": [
    {
      "title": ""
    }
  ]
}

DELETE ALL:
{
  "intent": "delete_task",
  "tasks": "all"
}

UPDATE ALL:
{
  "intent": "update_task",
  "action": "complete",
  "tasks": "all"
}

Rules:
- If multiple people or steps are mentioned, split them into separate tasks
- Each task must be clear and actionable
- Extract due dates like today, tomorrow, next week if mentioned
- If no due date, keep it empty
- update_task requires an action
- "complete" means mark completed = true
- "reopen" means mark completed = false
- If user says "all", "everything", use tasks = "all"
- If multiple tasks are mentioned, split them
- If task is referred by number, put it as a STRING in "task"
- Always include intent
- Always output valid JSON only
"""

def get_intent(user_text: str) -> dict:
    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"}
            },
            timeout=60
        )

        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        print("🔍 LLM RAW OUTPUT:", raw)
        parsed = json.loads(raw)
        return {
            "intent": parsed.get("intent", "").lower(),
            "task": str(parsed.get("task", "")),
            "due_date": parsed.get("due_date", ""),
            "tasks": parsed.get("tasks", []),
            "action": parsed.get("action", "")
        }

    except Exception as e:
        print("❌ Intent error:", e)
        return {"intent": "unknown", "task": "", "due_date": "", "tasks": [], "action": ""}