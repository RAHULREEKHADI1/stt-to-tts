from config.db import get_db
from bson import ObjectId
from datetime import datetime, date
import re

db = get_db()


def get_next_task_number(user_id):
    last = db.tasks.find(
        {"user_id": ObjectId(user_id)}
    ).sort("task_number", -1).limit(1)

    last = list(last)
    return last[0]["task_number"] + 1 if last else 1


def create_task(user_id, title, due_date=None, assignee=None):
    task_number = get_next_task_number(user_id)

    result = db.tasks.insert_one({
        "user_id": ObjectId(user_id),
        "task_number": task_number,
        "title": title,
        "assignee": assignee,
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.now()
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
        "title": {"$regex": title, "$options": "i"}
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
            "title": {"$regex": title, "$options": "i"}
        },
        {"$set": data}
    )

    if result.matched_count == 0:
        raise Exception("Task not found")


def get_tasks_by_due_date(user_id, due_date):
    return list(db.tasks.find({
        "user_id": ObjectId(user_id),
        "due_date": due_date
    }))


def toggle_task_completed_by_id(user_id: str, task_id: str) -> bool:
    try:
        task = db.tasks.find_one({
            "_id": ObjectId(task_id),
            "user_id": ObjectId(user_id)
        })
        if not task:
            return False

        new_status = not task.get("completed", False)
        result = db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"completed": new_status}}
        )
        return result.modified_count == 1
    except:
        return False


def delete_tasks_by_assignee(user_id, assignee):
    result = db.tasks.delete_many({
        "user_id": ObjectId(user_id),
        "assignee": {"$regex": f"^{assignee}$", "$options": "i"}
    })
    return result.deleted_count


def update_tasks_by_assignee(user_id, assignee, data):
    result = db.tasks.update_many(
        {
            "user_id": ObjectId(user_id),
            "assignee": {"$regex": f"^{assignee}$", "$options": "i"}
        },
        {"$set": data}
    )
    return result.modified_count


def get_tasks_by_assignee(user_id, assignee):
    """Get tasks by assignee"""
    return list(db.tasks.find({
        "user_id": ObjectId(user_id),
        "assignee": {"$regex": f"^{assignee}$", "$options": "i"}
    }).sort("task_number", 1))


def get_tasks_by_title_search(user_id, search_term):
    """Search tasks by title"""
    return list(db.tasks.find({
        "user_id": ObjectId(user_id),
        "title": {"$regex": search_term, "$options": "i"}
    }).sort("task_number", 1))


def update_task_title(user_id, task_number, new_title):
    """Update task title"""
    result = db.tasks.update_one(
        {
            "user_id": ObjectId(user_id),
            "task_number": task_number
        },
        {"$set": {"title": new_title}}
    )
    return result.modified_count > 0


def delete_all_tasks(user_id):
    """Delete all tasks for a user"""
    result = db.tasks.delete_many({"user_id": ObjectId(user_id)})
    return result.deleted_count


def complete_all_tasks(user_id, completed=True):
    """Mark all tasks as completed or not completed"""
    result = db.tasks.update_many(
        {"user_id": ObjectId(user_id)},
        {"$set": {"completed": completed}}
    )
    return result.modified_count


def complete_tasks_for_today(user_id):
    """Mark all tasks due today as completed"""
    today = date.today().strftime("%Y-%m-%d")
    result = db.tasks.update_many(
        {
            "user_id": ObjectId(user_id),
            "due_date": today
        },
        {"$set": {"completed": True}}
    )
    return result.modified_count


def get_task_by_number(user_id, task_number):
    """Get task by task number"""
    return db.tasks.find_one({
        "user_id": ObjectId(user_id),
        "task_number": task_number
    })


def delete_task_by_number_list(user_id, task_numbers):
    """Delete multiple tasks by their numbers"""
    # Sort in descending order
    task_numbers.sort(reverse=True)
    deleted_count = 0
    
    for task_number in task_numbers:
        result = db.tasks.delete_one({
            "user_id": ObjectId(user_id),
            "task_number": task_number
        })
        
        if result.deleted_count > 0:
            deleted_count += 1
            # Update task numbers for tasks after the deleted one
            db.tasks.update_many(
                {
                    "user_id": ObjectId(user_id),
                    "task_number": {"$gt": task_number}
                },
                {"$inc": {"task_number": -1}}
            )
    
    return deleted_count


def update_task_by_number_list(user_id, task_numbers, data):
    """Update multiple tasks by their numbers"""
    task_numbers.sort(reverse=True)
    updated_count = 0
    
    for task_number in task_numbers:
        result = db.tasks.update_one(
            {
                "user_id": ObjectId(user_id),
                "task_number": task_number
            },
            {"$set": data}
        )
        
        if result.matched_count > 0:
            updated_count += 1
    
    return updated_count


def get_tasks_due_today(user_id):
    """Get all tasks due today"""
    today = date.today().strftime("%Y-%m-%d")
    return list(db.tasks.find({
        "user_id": ObjectId(user_id),
        "due_date": today
    }).sort("task_number", 1))


def get_tasks_by_completion(user_id, completed=True):
    """Get tasks by completion status"""
    return list(db.tasks.find({
        "user_id": ObjectId(user_id),
        "completed": completed
    }).sort("task_number", 1))


def search_tasks(user_id, query):
    """Search tasks by various criteria"""
    # Try to parse as task number
    if re.match(r'^task\s*(\d+)$', query.lower()):
        task_num = int(re.search(r'(\d+)', query).group(1))
        task = get_task_by_number(user_id, task_num)
        return [task] if task else []
    
    if "complete all tasks for today" in query.lower():
        return get_tasks_due_today(user_id)
    
    return list(db.tasks.find({
        "user_id": ObjectId(user_id),
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"assignee": {"$regex": query, "$options": "i"}}
        ]
    }).sort("task_number", 1))