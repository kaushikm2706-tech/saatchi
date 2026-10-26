import os

BASE_URL = "https://api.meta.ai/v1"
SPARK_MODEL = "muse-spark-1.3"
SAM_MODEL = "sam-3.1"
VOICE_MODEL = "muse-voice-transcribe-1.0"
# Muse Image is intentionally never used: Meta's geographic policy blocks it from India.


def api_key() -> str:
    key = os.environ.get("MODEL_API_KEY", "")
    if not key:
        raise RuntimeError("Set MODEL_API_KEY (from dev.meta.ai) in your environment. Never hard-code it.")
    return key
