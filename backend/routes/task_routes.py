from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.task import get_tasks,toggle_task_completed_by_id
from config.db import get_db
from bson import ObjectId

task_bp = Blueprint("tasks", __name__)
db=get_db()

@task_bp.route("", methods=["GET"])
@task_bp.route("/", methods=["GET"])
@jwt_required()
def tasks():
    user_id = get_jwt_identity()
    
    raw_tasks = list(db.tasks.find({"user_id": ObjectId(user_id)}))

    cleaned_tasks = []
    for t in raw_tasks:
        task = dict(t)
        task["_id"] = str(t["_id"]) if "_id" in t else None
        
        if "user_id" in task:
            task["user_id"] = str(task["user_id"])
        
        task["completed"] = bool(task.get("completed", False))
        cleaned_tasks.append(task)

    return jsonify(cleaned_tasks)

@task_bp.route("/<task_id>/toggle", methods=["PATCH"])
@jwt_required()
def toggle_task(task_id):
    user_id = get_jwt_identity()

    try:
        task = db.tasks.find_one({"_id": ObjectId(task_id), "user_id": ObjectId(user_id)})
        if not task:
            return jsonify({"message": "Task not found"}), 404

        new_completed = not task.get("completed", False)
        db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"completed": new_completed}})

        return jsonify({"_id": str(task["_id"]), "completed": new_completed})

    except Exception as e:
        return jsonify({"message": str(e)}), 400


