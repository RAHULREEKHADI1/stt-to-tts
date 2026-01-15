from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
import re

from utils.audio import validate_audio, save_audio, convert_to_wav
from services.stt_service import speech_to_text
from services.intent_service import get_intent
from services.tool_service import parse_with_openai_tools
from services.tts_service import speak
from services.pinecone_service import store_task_embedding
from config.db import get_db
from bson import ObjectId
import json

from models.task import (
    create_task,
    get_tasks,
    delete_task_by_number,
    delete_task_by_title,
    update_task_by_number,
    update_task_by_title,
    delete_tasks_by_assignee,
    update_tasks_by_assignee,
    get_tasks_by_due_date,
    get_tasks_by_assignee,
    delete_all_tasks,
    complete_all_tasks,
    complete_tasks_for_today,
    get_task_by_number,
    delete_task_by_number_list,
    update_task_by_number_list,
    get_tasks_due_today,
    get_tasks_by_completion,
    search_tasks
)

db = get_db()

voice_bp = Blueprint("voice", __name__)


def process_create_operation(user_id, operation):
    """Process create task operation"""
    created_count = 0
    created_details = []
    
    tasks_to_create = operation.get("tasks", [])
    if not tasks_to_create and operation.get("task"):
        tasks_to_create = [{
            "title": operation.get("task"),
            "due_date": operation.get("due_date", ""),
            "assignee": operation.get("assignee", "")
        }]
    
    for task_data in tasks_to_create:
        title = task_data.get("title", "").strip()
        due_date = task_data.get("due_date", "")
        assignee = task_data.get("assignee", "")
        
        if not title or len(title) < 3:
            continue
            
        formatted_title = title
        if assignee:
            formatted_title = f"{title} (assigned to {assignee})"
        
        task_id, task_number = create_task(
            user_id,
            formatted_title,
            due_date,
            assignee
        )
        
        store_task_embedding(task_id, title, user_id, assignee)
        
        created_count += 1
        created_details.append({
            "task_number": task_number,
            "title": formatted_title,
            "assignee": assignee,
            "due_date": due_date
        })
    
    return created_count, created_details


def process_update_operation(user_id, operation):
    """Process update task operation"""
    updated_count = 0
    updated_details = []
    
    action = operation.get("action", "complete")
    task_numbers = operation.get("task_numbers", [])
    filter_data = operation.get("filter", {})
    new_title = operation.get("new_title", "")
    
    if action == "complete":
        set_data = {"completed": True}
    elif action == "reopen":
        set_data = {"completed": False}
    elif action == "update_title" and new_title:
        set_data = {"title": new_title}
    else:
        set_data = {}
    
    if filter_data.get("today") or action == "complete_today":
        today_tasks = get_tasks_due_today(user_id)
        task_numbers = [task["task_number"] for task in today_tasks]
        updated_count = complete_tasks_for_today(user_id)
        updated_details = task_numbers
    
    elif filter_data.get("all") or action == "complete_all":
        updated_count = complete_all_tasks(user_id, action == "complete_all")
        all_tasks = get_tasks(user_id)
        updated_details = [task["task_number"] for task in all_tasks]
    
    elif task_numbers:
        if set_data:  
            updated_count = update_task_by_number_list(user_id, task_numbers, set_data)
        updated_details = task_numbers
    
    elif filter_data.get("assignee"):
        assignee = filter_data["assignee"]
        updated_count = update_tasks_by_assignee(user_id, assignee, set_data)
        tasks = get_tasks_by_assignee(user_id, assignee)
        updated_details = [task["task_number"] for task in tasks]
    
    elif filter_data.get("due_date"):
        due_date = filter_data["due_date"]
        tasks = get_tasks_by_due_date(user_id, due_date)
        for task in tasks:
            update_task_by_number(user_id, task["task_number"], set_data)
            updated_details.append(task["task_number"])
        updated_count = len(tasks)
    
    else:
        tasks_to_update = operation.get("tasks", [])
        for task_data in tasks_to_update:
            title = task_data.get("title", "")
            assignee = task_data.get("assignee", "")
            
            query = {"user_id": ObjectId(user_id)}
            if title:
                query["title"] = {"$regex": title, "$options": "i"}
            if assignee:
                query["assignee"] = {"$regex": f"^{assignee}$", "$options": "i"}
            
            task = db.tasks.find_one(query)
            if task:
                update_task_by_number(user_id, task["task_number"], set_data)
                updated_count += 1
                updated_details.append(task["task_number"])
    
    return updated_count, updated_details, action


def process_delete_operation(user_id, operation):
    """Process delete task operation"""
    deleted_count = 0
    deleted_details = []
    
    task_numbers = operation.get("task_numbers", [])
    filter_data = operation.get("filter", {})
    
    if filter_data.get("all"):
        all_tasks = get_tasks(user_id)
        deleted_details = [t["task_number"] for t in all_tasks]
        deleted_count = delete_all_tasks(user_id)
    
    elif task_numbers:
        deleted_count = delete_task_by_number_list(user_id, task_numbers)
        deleted_details = task_numbers
    
    elif filter_data.get("assignee"):
        assignee = filter_data["assignee"]
        deleted_count = delete_tasks_by_assignee(user_id, assignee)
        deleted_details.append(f"assignee:{assignee}")
    
    elif filter_data.get("due_date"):
        due_date = filter_data["due_date"]
        tasks = get_tasks_by_due_date(user_id, due_date)
        for task in tasks:
            delete_task_by_number(user_id, task["task_number"])
            deleted_details.append(task["task_number"])
        deleted_count = len(tasks)
    
    else:
        tasks_to_delete = operation.get("tasks", [])
        for task_data in tasks_to_delete:
            title = task_data.get("title", "")
            assignee = task_data.get("assignee", "")
            
            query = {"user_id": ObjectId(user_id)}
            if title:
                query["title"] = {"$regex": title, "$options": "i"}
            if assignee:
                query["assignee"] = {"$regex": f"^{assignee}$", "$options": "i"}
            
            task = db.tasks.find_one(query)
            if task:
                delete_task_by_number(user_id, task["task_number"])
                deleted_count += 1
                deleted_details.append(task["task_number"])
    
    return deleted_count, deleted_details


def process_list_operation(user_id, operation):
    """Process list tasks operation"""
    filter_data = operation.get("filter", {})
    tasks = get_tasks(user_id)
    
    if filter_data.get("today"):
        tasks = get_tasks_due_today(user_id)
    
    if filter_data.get("assignee"):
        assignee = filter_data["assignee"]
        tasks = [t for t in tasks if t.get("assignee", "").lower() == assignee.lower()]
    
    if filter_data.get("due_date"):
        due_date = filter_data["due_date"]
        tasks = [t for t in tasks if t.get("due_date", "") == due_date]
    
    if filter_data.get("completed") is not None:
        tasks = [t for t in tasks if t.get("completed", False) == filter_data["completed"]]
    
    if filter_data.get("search"):
        search_query = filter_data["search"]
        tasks = search_tasks(user_id, search_query)
    
    return tasks


@voice_bp.route("/upload", methods=["POST"])
@jwt_required()
def voice_upload():
    """Enhanced voice endpoint with multi-task support"""
    user_id = get_jwt_identity()
    user_text = ""
    response_text = ""
    operation_results = []
    
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
        
        print(f"🎤 User said: {user_text}")
        
        openai_operations = parse_with_openai_tools(user_text)
        
        if openai_operations:
            print("🔧 Using OpenAI tool parsing")
            operations = openai_operations
            intent_type = "multi_intent"
        else:
            print("🔧 Using Mistral intent parsing")
            intent_data = get_intent(user_text)
            intent_type = intent_data.get("intent", "unknown")
            
            if intent_type == "multi_intent":
                operations = intent_data.get("operations", [])
            else:
                operation_data = {
                    "intent": intent_type,
                    "task": intent_data.get("task", ""),
                    "due_date": intent_data.get("due_date", ""),
                    "assignee": intent_data.get("assignee", ""),
                    "tasks": intent_data.get("tasks", []),
                    "action": intent_data.get("action", ""),
                    "new_title": intent_data.get("new_title", ""),
                    "task_numbers": intent_data.get("task_numbers", []),
                    "filter": intent_data.get("filter", {})
                }
                operations = [operation_data] if intent_type != "unknown" else []
        
        for i, operation in enumerate(operations):
            op_intent = operation.get("intent", "")
            result = {"intent": op_intent, "success": False}
            
            try:
                if op_intent == "create_task":
                    created_count, details = process_create_operation(user_id, operation)
                    result.update({
                        "success": created_count > 0,
                        "count": created_count,
                        "details": details,
                        "message": f"Created {created_count} task(s)"
                    })
                
                elif op_intent == "update_task":
                    updated_count, details, action = process_update_operation(user_id, operation)
                    action_text = action.replace("_", " ").title()
                    result.update({
                        "success": updated_count > 0,
                        "count": updated_count,
                        "details": details,
                        "action": action,
                        "message": f"{action_text} {updated_count} task(s)"
                    })
                
                elif op_intent == "delete_task":
                    deleted_count, details = process_delete_operation(user_id, operation)
                    result.update({
                        "success": deleted_count > 0,
                        "count": deleted_count,
                        "details": details,
                        "message": f"Deleted {deleted_count} task(s)"
                    })
                
                elif op_intent == "list_tasks":
                    tasks = process_list_operation(user_id, operation)
                    task_count = len(tasks)
                    
                    if task_count == 0:
                        message = "No tasks found"
                    elif task_count == 1:
                        task = tasks[0]
                        status = "completed" if task.get("completed", False) else "pending"
                        assignee_text = f" assigned to {task.get('assignee', '')}" if task.get("assignee") else ""
                        message = f"Found 1 task: {task.get('title', '')}{assignee_text} ({status})"
                    else:
                        completed = sum(1 for t in tasks if t.get("completed", False))
                        pending = task_count - completed
                        message = f"Found {task_count} tasks ({completed} completed, {pending} pending)"
                    
                    result.update({
                        "success": True,
                        "count": task_count,
                        "details": tasks,
                        "message": message
                    })
                
                elif op_intent == "small_talk":
                    greetings = ["Hi", "Hello", "Hey there", "Greetings"]
                    import random
                    greeting = random.choice(greetings)
                    result.update({
                        "success": True,
                        "message": f"{greeting}! How can I help you with your tasks today?"
                    })
                
                else:
                    result.update({
                        "success": False,
                        "message": f"I didn't understand that. Please try again with a task-related request."
                    })
                
            except Exception as e:
                result.update({
                    "success": False,
                    "message": f"Error processing {op_intent}: {str(e)}",
                    "error": True
                })
            
            operation_results.append(result)
        
        if len(operation_results) == 1:
            response_text = operation_results[0]["message"]
        else:
            successful_ops = [op["message"] for op in operation_results if op["success"]]
            if successful_ops:
                response_text = " ".join(successful_ops)
            else:
                response_text = "I couldn't process any of your requests. Please try again."
        
        audio_filename = f"response_{user_id}_{ObjectId()}.wav"
        audio_path = speak(response_text, audio_filename)
        
        return jsonify({
            "user_text": user_text,
            "response_text": response_text,
            "operations": operation_results,
            "audio_url": audio_path,
            "success": any(op["success"] for op in operation_results)
        })
        
    except Exception as e:
        response_text = f"I encountered an error: {str(e)}"
        
        audio_filename = f"error_{user_id}_{ObjectId()}.wav"
        audio_path = speak(response_text, audio_filename)
        
        return jsonify({
            "user_text": user_text,
            "response_text": response_text,
            "operations": [],
            "audio_url": audio_path,
            "success": False,
            "error": True
        }), 400