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

JSON format:
{
  "intent": "",
  "task": "",
  "due_date": ""
}

Rules:
- If task is referred by number, put it as a STRING in "task"
- If task is referred by title, put title in "task"
- Output only JSON
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
            "due_date": parsed.get("due_date", "")
        }

    except Exception as e:
        print("❌ Intent error:", e)
        return {"intent": "unknown", "task": "", "due_date": ""}
