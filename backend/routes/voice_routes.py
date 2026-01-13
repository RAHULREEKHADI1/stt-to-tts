from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from utils.audio import validate_audio, save_audio, convert_to_wav
from services.stt_service import speech_to_text
from services.intent_service import get_intent
from services.tts_service import speak
from services.pinecone_service import store_task_embedding

from models.task import (
    create_task,
    get_tasks,
    delete_task_by_number,
    delete_task_by_title,
    update_task_by_number,
    update_task_by_title
)

voice_bp = Blueprint("voice", __name__)


@voice_bp.route("/upload", methods=["POST"])
@jwt_required()
def voice_upload():
    user_id = get_jwt_identity()

    if "audio" not in request.files:
        return jsonify({"message": "No audio provided"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"message": "Empty audio"}), 400

    try:
        validate_audio(audio_file)
        raw = save_audio(audio_file)
        wav = convert_to_wav(raw)

        stt = speech_to_text(wav)
        user_text = stt["text"]

        intent = get_intent(user_text)
        response_text = "Sorry, I didn’t understand."

        # -------- NORMALIZE TASK FIELD --------
        task_raw = intent.get("task")
        task_number = None
        task_title = None

        if isinstance(task_raw, str) and task_raw.isdigit():
            task_number = int(task_raw)
        elif isinstance(task_raw, str) and task_raw:
            task_title = task_raw

        # -------- CREATE --------
        if intent["intent"] == "create_task":
            task_id, num = create_task(
                user_id,
                intent["task"],
                intent.get("due_date")
            )
            store_task_embedding(task_id, intent["task"], user_id)
            response_text = f"Task number {num} created."

        # -------- DELETE --------
        elif intent["intent"] == "delete_task":
            if task_number:
                delete_task_by_number(user_id, task_number)
                response_text = f"Task number {task_number} deleted."
            elif task_title:
                delete_task_by_title(user_id, task_title)
                response_text = f"Task '{task_title}' deleted."
            else:
                response_text = "Please specify a task number or title."

        # -------- UPDATE --------
        elif intent["intent"] == "update_task":
            if task_number:
                update_task_by_number(user_id, task_number, {"completed": True})
                response_text = f"Task number {task_number} completed."
            elif task_title:
                update_task_by_title(user_id, task_title, {"completed": True})
                response_text = f"Task '{task_title}' completed."
            else:
                response_text = "Please specify a task number or title."

        # -------- LIST --------
        elif intent["intent"] == "list_tasks":
            tasks = get_tasks(user_id)
            if not tasks:
                response_text = "You have no tasks."
            else:
                response_text = "Your tasks are: " + ", ".join(
                    [f"{t['task_number']}. {t['title']}" for t in tasks]
                )

        audio_path = speak(response_text, f"{user_id}.wav")

        return jsonify({
            "user_text": user_text,
            "response_text": response_text,
            "audio_url": audio_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
