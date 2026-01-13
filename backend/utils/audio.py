import os
import subprocess
import uuid

ALLOWED_EXTENSIONS = {"wav", "webm","mp3"}
MAX_FILE_SIZE_MB = 10


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_audio(file):
    if not allowed_file(file.filename):
        raise ValueError("Unsupported audio format")

    file.seek(0, os.SEEK_END)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)

    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError("Audio file too large")


def save_audio(file):
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    path = f"/tmp/{filename}"
    file.save(path)
    return path


def convert_to_wav(input_path):
    if input_path.endswith(".wav"):
        return input_path

    output_path = input_path.rsplit(".", 1)[0] + ".wav"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-ar",
            "16000",
            "-ac",
            "1",
            output_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    return output_path
