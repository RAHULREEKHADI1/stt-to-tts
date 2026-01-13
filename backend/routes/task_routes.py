from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.task import get_tasks
from config.db import get_db
from bson import ObjectId

task_bp = Blueprint("tasks", __name__)
db=get_db()

@task_bp.route("", methods=["GET"])
@task_bp.route("/", methods=["GET"])
@jwt_required()
def tasks():
    user_id = get_jwt_identity()
    tasks = get_tasks(user_id)

    cleaned_tasks = []
    for t in tasks:
        task = dict(t)

        if "_id" in task:
            task["_id"] = str(task["_id"])

        if "user_id" in task:
            task["user_id"] = str(task["user_id"])
        
        task["completed"] = bool(task.get("completed", False))

        cleaned_tasks.append(task)

    return jsonify(cleaned_tasks)


