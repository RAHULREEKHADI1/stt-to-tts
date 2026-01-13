from TTS.api import TTS
import os

tts = TTS("tts_models/en/vctk/vits")

BASE_PATH = "storage/audio_responses"
DEFAULT_SPEAKER = "p225" 


def speak(text, filename):
    os.makedirs(BASE_PATH, exist_ok=True)
    path = os.path.join(BASE_PATH, filename)

    tts.tts_to_file(
        text=text,
        file_path=path,
        speaker=DEFAULT_SPEAKER
    )

    return path
