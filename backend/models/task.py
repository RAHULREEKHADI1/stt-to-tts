from config.db import get_db
from bson import ObjectId

db = get_db()


def get_next_task_number(user_id):
    last = db.tasks.find(
        {"user_id": ObjectId(user_id)}
    ).sort("task_number", -1).limit(1)

    last = list(last)
    return last[0]["task_number"] + 1 if last else 1


def create_task(user_id, title, due_date=None):
    task_number = get_next_task_number(user_id)

    result = db.tasks.insert_one({
        "user_id": ObjectId(user_id),
        "task_number": task_number,
        "title": title,
        "due_date": due_date,
        "completed": False
    })

    return str(result.inserted_id), task_number


def get_tasks(user_id):
    return list(
        db.tasks.find(
            {"user_id": ObjectId(user_id)},
            {"_id": 0}
        ).sort("task_number", 1)
    )


def delete_task_by_number(user_id, task_number):
    result = db.tasks.delete_one({
        "user_id": ObjectId(user_id),
        "task_number": task_number
    })

    if result.deleted_count == 0:
        raise Exception("Task not found")

    # reindex numbers
    db.tasks.update_many(
        {
            "user_id": ObjectId(user_id),
            "task_number": {"$gt": task_number}
        },
        {"$inc": {"task_number": -1}}
    )


def delete_task_by_title(user_id, title):
    result = db.tasks.delete_one({
        "user_id": ObjectId(user_id),
        "title": {"$regex": f"^{title}$", "$options": "i"}
    })

    if result.deleted_count == 0:
        raise Exception("Task not found")


def update_task_by_number(user_id, task_number, data):
    result = db.tasks.update_one(
        {
            "user_id": ObjectId(user_id),
            "task_number": task_number
        },
        {"$set": data}
    )

    if result.matched_count == 0:
        raise Exception("Task not found")


def update_task_by_title(user_id, title, data):
    result = db.tasks.update_one(
        {
            "user_id": ObjectId(user_id),
            "title": {"$regex": f"^{title}$", "$options": "i"}
        },
        {"$set": data}
    )

    if result.matched_count == 0:
        raise Exception("Task not found")
