import os
from datetime import datetime
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from bson import ObjectId
from typing import List, Dict, Any, Optional

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")

if not api_key:
    raise RuntimeError("PINECONE_API_KEY not set")

pc = Pinecone(api_key=api_key)

INDEX_NAME = "voice-ai"

existing_indexes = pc.list_indexes()
if INDEX_NAME not in [i.name for i in existing_indexes]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
    )

index = pc.Index(INDEX_NAME)

embedder = SentenceTransformer("all-MiniLM-L6-v2")


def store_task_embedding(task_id: str, text: str, user_id: str, assignee: str = "", 
                         task_number: Optional[int] = None, due_date: str = "", 
                         completed: bool = False):
    """
    Stores task embedding in Pinecone with enhanced metadata
    """
    embedding = embedder.encode(text).tolist()
    
    metadata = {
        "user_id": str(user_id),
        "text": text,
        "assignee": assignee or "",
        "task_id": str(task_id),
        "due_date": due_date,
        "completed": str(completed),
        "created_at": datetime.now().isoformat()
    }
    
    if task_number is not None:
        metadata["task_number"] = str(task_number)
    
    index.upsert(
        vectors=[
            {
                "id": str(task_id),
                "values": embedding,
                "metadata": metadata
            }
        ]
    )


def update_task_embedding(task_id: str, text: str = None, assignee: str = None, 
                          completed: bool = None, due_date: str = None):
    """
    Update an existing task embedding in Pinecone
    """
    try:
        fetch_result = index.fetch(ids=[task_id])
        
        if task_id not in fetch_result.vectors:
            return False
        
        existing_vector = fetch_result.vectors[task_id]
        metadata = existing_vector.metadata.copy()
        
        if text is not None:
            metadata["text"] = text
        
        if assignee is not None:
            metadata["assignee"] = assignee
        
        if completed is not None:
            metadata["completed"] = str(completed)
        
        if due_date is not None:
            metadata["due_date"] = due_date
        
        if text is not None:
            new_embedding = embedder.encode(text).tolist()
        else:
            new_embedding = existing_vector.values
        
        index.upsert(
            vectors=[
                {
                    "id": task_id,
                    "values": new_embedding,
                    "metadata": metadata
                }
            ]
        )
        return True
    except Exception as e:
        print(f"❌ Error updating task embedding: {e}")
        return False


def delete_task_embedding(task_id: str):
    """
    Delete a task embedding from Pinecone
    """
    try:
        index.delete(ids=[task_id])
        return True
    except Exception as e:
        print(f"❌ Error deleting task embedding: {e}")
        return False


def delete_user_tasks_embeddings(user_id: str):
    """
    Delete all task embeddings for a specific user
    """
    try:
        query_result = index.query(
            vector=[0] * 384,  
            filter={"user_id": str(user_id)},
            top_k=10000,
            include_metadata=True
        )
        
        task_ids = [match.id for match in query_result.matches]
        
        if task_ids:
            index.delete(ids=task_ids)
        
        return len(task_ids)
    except Exception as e:
        print(f"❌ Error deleting user task embeddings: {e}")
        return 0


def search_similar_tasks(user_id: str, query: str, top_k: int = 5, 
                         filter_by_assignee: str = None, 
                         filter_by_completed: bool = None):
    """
    Search for similar tasks using semantic search
    """
    try:
        query_embedding = embedder.encode(query).tolist()
        
        filter_query = {"user_id": str(user_id)}
        
        if filter_by_assignee:
            filter_query["assignee"] = filter_by_assignee
        
        if filter_by_completed is not None:
            filter_query["completed"] = str(filter_by_completed)
        
        results = index.query(
            vector=query_embedding,
            filter=filter_query,
            top_k=top_k,
            include_metadata=True
        )
        
        similar_tasks = []
        for match in results.matches:
            similar_tasks.append({
                "task_id": match.metadata.get("task_id"),
                "task_number": match.metadata.get("task_number"),
                "text": match.metadata.get("text"),
                "assignee": match.metadata.get("assignee", ""),
                "due_date": match.metadata.get("due_date", ""),
                "completed": match.metadata.get("completed", "False") == "True",
                "similarity_score": match.score
            })
        
        return similar_tasks
    except Exception as e:
        print(f"❌ Error searching similar tasks: {e}")
        return []


def get_tasks_by_assignee_from_pinecone(user_id: str, assignee: str):
    """
    Get tasks by assignee from Pinecone
    """
    try:
        results = index.query(
            vector=[0] * 384,
            filter={
                "user_id": str(user_id),
                "assignee": assignee
            },
            top_k=10000,
            include_metadata=True
        )
        
        tasks = []
        for match in results.matches:
            tasks.append({
                "task_id": match.metadata.get("task_id"),
                "task_number": match.metadata.get("task_number"),
                "text": match.metadata.get("text"),
                "assignee": match.metadata.get("assignee", ""),
                "due_date": match.metadata.get("due_date", ""),
                "completed": match.metadata.get("completed", "False") == "True"
            })
        
        return tasks
    except Exception as e:
        print(f"❌ Error getting tasks by assignee: {e}")
        return []


def get_tasks_due_today_from_pinecone(user_id: str):
    """
    Get tasks due today from Pinecone
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        results = index.query(
            vector=[0] * 384,  # Dummy vector
            filter={
                "user_id": str(user_id),
                "due_date": today
            },
            top_k=10000,
            include_metadata=True
        )
        
        tasks = []
        for match in results.matches:
            tasks.append({
                "task_id": match.metadata.get("task_id"),
                "task_number": match.metadata.get("task_number"),
                "text": match.metadata.get("text"),
                "assignee": match.metadata.get("assignee", ""),
                "due_date": match.metadata.get("due_date", ""),
                "completed": match.metadata.get("completed", "False") == "True"
            })
        
        return tasks
    except Exception as e:
        print(f"❌ Error getting today's tasks: {e}")
        return []


def complete_tasks_for_today_in_pinecone(user_id: str):
    """
    Mark all tasks due today as completed in Pinecone
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Query today's tasks
        results = index.query(
            vector=[0] * 384,  # Dummy vector
            filter={
                "user_id": str(user_id),
                "due_date": today
            },
            top_k=10000,
            include_metadata=True
        )
        
        updated_count = 0
        for match in results.matches:
            metadata = match.metadata.copy()
            metadata["completed"] = "True"
            
            # Update the vector
            index.upsert(
                vectors=[
                    {
                        "id": match.id,
                        "values": match.values,
                        "metadata": metadata
                    }
                ]
            )
            updated_count += 1
        
        return updated_count
    except Exception as e:
        print(f"❌ Error completing today's tasks in Pinecone: {e}")
        return 0


def complete_all_tasks_in_pinecone(user_id: str):
    """
    Mark all tasks as completed in Pinecone
    """
    try:
        # Query all tasks for user
        results = index.query(
            vector=[0] * 384,  # Dummy vector
            filter={"user_id": str(user_id)},
            top_k=10000,
            include_metadata=True
        )
        
        updated_count = 0
        for match in results.matches:
            metadata = match.metadata.copy()
            metadata["completed"] = "True"
            
            # Update the vector
            index.upsert(
                vectors=[
                    {
                        "id": match.id,
                        "values": match.values,
                        "metadata": metadata
                    }
                ]
            )
            updated_count += 1
        
        return updated_count
    except Exception as e:
        print(f"❌ Error completing all tasks in Pinecone: {e}")
        return 0


def get_task_by_number_from_pinecone(user_id: str, task_number: int):
    """
    Get task by task number from Pinecone
    """
    try:
        results = index.query(
            vector=[0] * 384,  # Dummy vector
            filter={
                "user_id": str(user_id),
                "task_number": str(task_number)
            },
            top_k=1,
            include_metadata=True
        )
        
        if results.matches:
            match = results.matches[0]
            return {
                "task_id": match.metadata.get("task_id"),
                "task_number": match.metadata.get("task_number"),
                "text": match.metadata.get("text"),
                "assignee": match.metadata.get("assignee", ""),
                "due_date": match.metadata.get("due_date", ""),
                "completed": match.metadata.get("completed", "False") == "True"
            }
        
        return None
    except Exception as e:
        print(f"❌ Error getting task by number from Pinecone: {e}")
        return None


def delete_tasks_by_numbers_from_pinecone(user_id: str, task_numbers: List[int]):
    """
    Delete multiple tasks by their numbers from Pinecone
    """
    try:
        # Convert task numbers to strings for filtering
        task_number_strs = [str(num) for num in task_numbers]
        
        # Query tasks with these numbers
        results = index.query(
            vector=[0] * 384,  # Dummy vector
            filter={
                "user_id": str(user_id),
                "task_number": {"$in": task_number_strs}
            },
            top_k=10000,
            include_metadata=True
        )
        
        task_ids = [match.id for match in results.matches]
        
        if task_ids:
            index.delete(ids=task_ids)
        
        return len(task_ids)
    except Exception as e:
        print(f"❌ Error deleting tasks by numbers from Pinecone: {e}")
        return 0


def batch_update_tasks_in_pinecone(user_id: str, task_numbers: List[int], 
                                   updates: Dict[str, Any]):
    """
    Batch update multiple tasks in Pinecone
    """
    try:
        # Convert task numbers to strings for filtering
        task_number_strs = [str(num) for num in task_numbers]
        
        # Query tasks with these numbers
        results = index.query(
            vector=[0] * 384,  # Dummy vector
            filter={
                "user_id": str(user_id),
                "task_number": {"$in": task_number_strs}
            },
            top_k=10000,
            include_metadata=True
        )
        
        updated_vectors = []
        for match in results.matches:
            metadata = match.metadata.copy()
            
            # Apply updates
            if "completed" in updates:
                metadata["completed"] = str(updates["completed"])
            
            if "assignee" in updates:
                metadata["assignee"] = updates["assignee"]
            
            if "due_date" in updates:
                metadata["due_date"] = updates["due_date"]
            
            if "text" in updates:
                metadata["text"] = updates["text"]
                # Re-embed if text changed
                new_embedding = embedder.encode(updates["text"]).tolist()
            else:
                new_embedding = match.values
            
            updated_vectors.append({
                "id": match.id,
                "values": new_embedding,
                "metadata": metadata
            })
        
        if updated_vectors:
            index.upsert(vectors=updated_vectors)
        
        return len(updated_vectors)
    except Exception as e:
        print(f"❌ Error batch updating tasks in Pinecone: {e}")
        return 0


def semantic_search_tasks(user_id: str, query: str, 
                         filter_by_completed: Optional[bool] = None,
                         filter_by_assignee: Optional[str] = None,
                         filter_by_due_date: Optional[str] = None,
                         top_k: int = 10):
    """
    Enhanced semantic search with multiple filters
    """
    try:
        query_embedding = embedder.encode(query).tolist()
        
        filter_query = {"user_id": str(user_id)}
        
        if filter_by_completed is not None:
            filter_query["completed"] = str(filter_by_completed)
        
        if filter_by_assignee:
            filter_query["assignee"] = filter_by_assignee
        
        if filter_by_due_date:
            filter_query["due_date"] = filter_by_due_date
        
        results = index.query(
            vector=query_embedding,
            filter=filter_query,
            top_k=top_k,
            include_metadata=True
        )
        
        formatted_results = []
        for match in results.matches:
            formatted_results.append({
                "task_id": match.metadata.get("task_id"),
                "task_number": match.metadata.get("task_number", "Unknown"),
                "title": match.metadata.get("text", ""),
                "assignee": match.metadata.get("assignee", ""),
                "due_date": match.metadata.get("due_date", ""),
                "completed": match.metadata.get("completed", "False") == "True",
                "similarity_score": round(match.score, 4)
            })
        
        return formatted_results
    except Exception as e:
        print(f"❌ Error in semantic search: {e}")
        return []