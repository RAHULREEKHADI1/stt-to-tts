
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer


load_dotenv() 

api_key = os.getenv("PINECONE_API_KEY")

if not api_key:
    raise RuntimeError("PINECONE_API_KEY not set")

pc = Pinecone(api_key=api_key)

INDEX_NAME = "voice-ai"

if INDEX_NAME not in [i["name"] for i in pc.list_indexes()]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
    )

index = pc.Index(INDEX_NAME)

embedder = SentenceTransformer("all-MiniLM-L6-v2")


def store_task_embedding(task_id, text, user_id):
    """
    Stores task embedding in Pinecone
    """
    embedding = embedder.encode(text).tolist()

    index.upsert(
        vectors=[
            {
                "id": str(task_id),
                "values": embedding,
                "metadata": {
                    "user_id": str(user_id),
                    "text": text
                }
            }
        ]
    )
