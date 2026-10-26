# Saatchi (சாட்சி, "witness")

Checks what a worker *says* they did against what the *video* shows. Narration (Tamil/English) -> Muse Voice Transcribe
-> claims (Muse Spark 1.3) -> two evidence channels (Spark video reasoning, SAM 3.1 object tracks) -> SUPPORTED / CONTRADICTED /
UNVERIFIABLE -> bilingual report + requests for missing proof. When the channels disagree it abstains.

Status: skeleton, tested with mocks only. Real API behaviour is unverified until a live run (see BUILD_LOG.md).

## Run (needs your own key from dev.meta.ai; calls are billed to your credits)
    pip install -r requirements.txt
    export MODEL_API_KEY=LLM_...        # Windows PowerShell: $env:MODEL_API_KEY="LLM_..."
    python -m pytest -q                 # mocked tests, no API calls
    python -m saatchi.cli sam-probe clip.mp4 "bolt" --live
    python -m saatchi.cli run clip.mp4 --live
Requires ffmpeg on PATH. Muse Image is not used (blocked from India).
