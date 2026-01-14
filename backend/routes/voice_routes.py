from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from utils.audio import validate_audio, save_audio, convert_to_wav
from services.stt_service import speech_to_text
from services.intent_service import get_intent
from services.tts_service import speak
from services.pinecone_service import store_task_embedding
from config.db import get_db
from bson import ObjectId

db = get_db()

from models.task import (
    create_task,
    get_tasks,
    delete_task_by_number,
    delete_task_by_title,
    update_task_by_number,
    update_task_by_title
)

def is_noise_title(title):
    noise_phrases = [
        "mark",
        "complete",
        "completed",
        "delete",
        "remove",
        "update",
        "task",
        "tasks",
        "list",
        "show"
    ]
    title = title.lower().strip()
    return len(title.split()) <= 4 and any(n in title for n in noise_phrases)


voice_bp = Blueprint("voice", __name__)

@voice_bp.route("/upload", methods=["POST"])
@jwt_required()
def voice_upload():
    user_id = get_jwt_identity()
    user_text = ""
    response_text = ""
    updated_items = []

    try:
        if "audio" not in request.files:
            raise Exception("No audio provided")
        audio_file = request.files["audio"]
        if audio_file.filename == "":
            raise Exception("Empty audio")

        validate_audio(audio_file)
        raw = save_audio(audio_file)
        wav = convert_to_wav(raw)
        stt = speech_to_text(wav)
        user_text = stt["text"]

        intent = get_intent(user_text)
        response_text = "Sorry, I didn’t understand."

        task_raw = intent.get("task")
        task_number = None
        task_title = None
        if isinstance(task_raw, str) and task_raw.isdigit():
            task_number = int(task_raw)
        elif isinstance(task_raw, str) and task_raw:
            task_title = task_raw

        tasks_from_llm = intent.get("tasks", [])

        if intent["intent"] == "create_task":
            tasks_to_create = tasks_from_llm if tasks_from_llm else [{"title": intent.get("task"), "due_date": intent.get("due_date")}]
            created = 0
            for t in tasks_to_create:
                title = t.get("title")
                assignee = t.get("assignee")
                due_date = t.get("due_date")
                if assignee:
                    title = f"{title} (assigned to {assignee})"
                task_id, num = create_task(user_id, title, due_date)
                store_task_embedding(task_id, title, user_id)
                created += 1
            response_text = f"{created} tasks created." if created > 1 else "Task created."

        elif intent["intent"] == "delete_task":
            deleted = 0
            deleted_items = []
            tasks_field = intent.get("tasks")
            due_date = intent.get("due_date")

            if due_date:
                tasks = list(db.tasks.find({
                    "user_id": ObjectId(user_id),
                    "due_date": due_date
                }))
                for t in tasks:
                    delete_task_by_number(user_id, t["task_number"])
                    deleted_items.append(t["task_number"])
                    deleted += 1
                response_text = f"All {due_date.replace('_', ' ')} tasks deleted." if deleted else "No matching tasks found."
            elif tasks_field == "all":
                tasks = get_tasks(user_id)
                deleted_items = [t["task_number"] for t in tasks]
                db.tasks.delete_many({"user_id": ObjectId(user_id)})
                response_text = "All tasks deleted."
            elif isinstance(tasks_field, list) and tasks_field:
                for t in tasks_field:
                    title = t.get("title")
                    if title:
                        delete_task_by_title(user_id, title)
                        deleted_items.append(title)
                        deleted += 1
                response_text = f"{deleted} tasks deleted." if deleted else "No matching tasks found."
            else:
                task = intent.get("task")
                if task and task.isdigit():
                    delete_task_by_number(user_id, int(task))
                    deleted_items.append(int(task))
                    deleted = 1
                elif task:
                    delete_task_by_title(user_id, task)
                    deleted_items.append(task)
                    deleted = 1
                response_text = "Task deleted." if deleted == 1 else "Please specify a task."

        elif intent["intent"] == "update_task":
            updated_count = 0
            action = intent.get("action", "complete")
            due_date = intent.get("due_date")
            completed_value = True if action == "complete" else False
            tasks_field = intent.get("tasks")
            task = intent.get("task")

            if due_date:
                tasks = list(db.tasks.find({
                    "user_id": ObjectId(user_id),
                    "due_date": due_date
                }))
                for t in tasks:
                    update_task_by_number(
                        user_id,
                        t["task_number"],
                        {"completed": completed_value}
                    )
                    updated_items.append(t["task_number"])
                    updated_count += 1
                response_text = (
                    f"All {due_date.replace('_', ' ')} tasks marked as completed."
                    if completed_value else
                    f"All {due_date.replace('_', ' ')} tasks reopened."
                ) if updated_count else "No matching tasks found."
            elif tasks_field == "all":
                result = db.tasks.update_many({"user_id": ObjectId(user_id)}, {"$set": {"completed": completed_value}})
                updated_count = result.modified_count
                updated_items = ["all"]
                response_text = "All tasks marked as completed." if completed_value else "All tasks reopened."
            elif isinstance(tasks_field, list) and tasks_field:
                for t in tasks_field:
                    title = t.get("title")
                    if title and not is_noise_title(title):
                        task_doc = db.tasks.find_one({"user_id": ObjectId(user_id), "title": {"$regex": title, "$options": "i"}})
                        if task_doc:
                            update_task_by_number(user_id, task_doc["task_number"], {"completed": completed_value})
                            updated_items.append(task_doc["task_number"])
                            updated_count += 1
                response_text = f"{updated_count} tasks marked as completed." if completed_value else f"{updated_count} tasks reopened." if updated_count else "No matching tasks found."
            else:
                if task and task.isdigit():
                    update_task_by_number(user_id, int(task), {"completed": completed_value})
                    updated_items.append(int(task))
                    updated_count = 1
                    response_text = "Task marked as completed." if completed_value else "Task reopened."
                elif task:
                    task_doc = db.tasks.find_one({"user_id": ObjectId(user_id), "title": {"$regex": task, "$options": "i"}})
                    if task_doc:
                        update_task_by_number(user_id, task_doc["task_number"], {"completed": completed_value})
                        updated_items.append(task_doc["task_number"])
                        updated_count = 1
                        response_text = "Task marked as completed." if completed_value else "Task reopened."
                    else:
                        response_text = "Task not found."
                else:
                    response_text = "Please specify a task."

        elif intent["intent"] == "list_tasks":
            tasks = get_tasks(user_id)
            if not tasks:
                response_text = "You have no tasks."
            else:
                response_text = "Your tasks are: " + ", ".join([f"{t['task_number']}. {t['title']}" for t in tasks])

    except Exception as e:
        response_text = str(e)

    audio_path = speak(response_text, f"{user_id}.wav")

    return jsonify({
        "user_text": user_text,
        "response_text": response_text,
        "updated": updated_items,
        "audio_url": audio_path
    })