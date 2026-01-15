import openai
import json
from typing import List, Dict, Any

TASK_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_tasks",
            "description": "Create one or multiple tasks with title, due date, and assignee",
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Task title"},
                                "due_date": {"type": "string", "description": "Due date (today, tomorrow, YYYY-MM-DD)"},
                                "assignee": {"type": "string", "description": "Person assigned to task"}
                            },
                            "required": ["title"]
                        }
                    }
                },
                "required": ["tasks"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_tasks",
            "description": "Update one or multiple tasks (mark complete, reopen, change title)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["complete", "reopen", "update_title", "complete_all", "complete_today"],
                        "description": "Action to perform on tasks"
                    },
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Task title to update"},
                                "task_number": {"type": "integer", "description": "Task number to update"},
                                "assignee": {"type": "string", "description": "Assignee filter"},
                                "due_date": {"type": "string", "description": "Due date filter"},
                                "new_title": {"type": "string", "description": "New title if action is update_title"}
                            }
                        }
                    },
                    "filter": {
                        "type": "object",
                        "properties": {
                            "assignee": {"type": "string"},
                            "due_date": {"type": "string"},
                            "completed": {"type": "boolean"},
                            "all": {"type": "boolean", "description": "All tasks"},
                            "today": {"type": "boolean", "description": "Tasks due today"}
                        }
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_tasks",
            "description": "Delete one or multiple tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "task_number": {"type": "integer"},
                                "assignee": {"type": "string"},
                                "due_date": {"type": "string"}
                            }
                        }
                    },
                    "filter": {
                        "type": "object",
                        "properties": {
                            "assignee": {"type": "string"},
                            "due_date": {"type": "string"},
                            "all": {"type": "boolean", "description": "Delete all tasks"},
                            "task_numbers": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Specific task numbers to delete"
                            }
                        }
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List tasks with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "object",
                        "properties": {
                            "assignee": {"type": "string"},
                            "due_date": {"type": "string"},
                            "completed": {"type": "boolean"},
                            "today": {"type": "boolean", "description": "Tasks due today"},
                            "search": {"type": "string", "description": "Search in title or assignee"}
                        }
                    }
                }
            }
        }
    }
]


def parse_with_openai_tools(user_text: str) -> List[Dict]:
    """
    Use OpenAI tool calling to parse complex multi-task requests
    Returns a list of tool calls to execute
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "Parse the user's task management request and call appropriate functions. Extract task numbers when mentioned (like 'task 1', 'task number 3', etc.)."},
                {"role": "user", "content": user_text}
            ],
            tools=TASK_TOOLS,
            tool_choice="auto"
        )

        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            return []

        parsed_operations = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "create_tasks":
                parsed_operations.append({
                    "intent": "create_task",
                    "tasks": function_args.get("tasks", [])
                })
            elif function_name == "update_tasks":
                action = function_args.get("action")
                filter_data = function_args.get("filter", {})
                
                if action == "complete_all":
                    filter_data["all"] = True
                elif action == "complete_today":
                    filter_data["today"] = True
                
                parsed_operations.append({
                    "intent": "update_task",
                    "action": action,
                    "tasks": function_args.get("tasks", []),
                    "filter": filter_data
                })
            elif function_name == "delete_tasks":
                filter_data = function_args.get("filter", {})
                tasks_data = function_args.get("tasks", [])
                
                task_numbers = []
                for task in tasks_data:
                    if "task_number" in task:
                        task_numbers.append(task["task_number"])
                
                if task_numbers:
                    filter_data["task_numbers"] = task_numbers
                
                parsed_operations.append({
                    "intent": "delete_task",
                    "tasks": tasks_data,
                    "filter": filter_data
                })
            elif function_name == "list_tasks":
                parsed_operations.append({
                    "intent": "list_tasks",
                    "filter": function_args.get("filter", {})
                })

        return parsed_operations

    except Exception as e:
        print(f"❌ OpenAI tool parsing error: {e}")
        return []