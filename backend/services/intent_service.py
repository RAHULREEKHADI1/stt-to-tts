import subprocess
import json

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

JSON format:
{
  "intent": "",
  "task": "",
  "due_date": ""
}

Rules:
- If task is referred by number, put it as a STRING in "task" (example: "1")
- If task is referred by title, put title in "task"
- Output only JSON
"""

def get_intent(user_text: str) -> dict:
    prompt = f"""
{SYSTEM_PROMPT}

Text: "{user_text}"
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", "--format", "json"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=30
        )

        raw = result.stdout.strip()
        print("🔍 LLM RAW OUTPUT:", raw)

        parsed = json.loads(raw)

        parsed["intent"] = parsed.get("intent", "").strip().lower()
        parsed["task"] = str(parsed.get("task", "")).strip()

        return parsed

    except Exception as e:
        print("❌ Intent error:", e)
        return {"intent": "unknown"}
