def build_prompt(text):
    return f"""
You are an intent classifier.
Return ONLY JSON.

User input: "{text}"

Format:
{{
  "intent": "",
  "task": "",
  "due_date": ""
}}
"""
