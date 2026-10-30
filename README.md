# Saatchi (சாட்சி, "witness")

Checks what a worker *says* they did against what the *video* shows. Narration (Tamil/English) -> Muse Voice Transcribe
-> claims (Muse Spark 1.3) -> two evidence channels (Spark video reasoning, SAM 3.1 object tracks) -> SUPPORTED / CONTRADICTED /
UNVERIFIABLE -> bilingual report + requests for missing proof. When the channels disagree it abstains.

Status: built and unit-tested with mocks (18 tests). Real API behaviour is unverified until a live run (see BUILD_LOG.md).

## Setup (needs your own key from dev.meta.ai; live calls are billed to your credits)
    pip install -r requirements.txt
    export MODEL_API_KEY=LLM_...        # PowerShell: $env:MODEL_API_KEY="LLM_..."
    python -m pytest -q                 # mocked, no API calls
Requires ffmpeg and ffprobe on PATH. Muse Image is not used (blocked from India).

## Commands
    python -m saatchi.cli sam-probe clip.mp4 "bolt" --live   # one SAM call; saves sam_probe.raw.txt
    python -m saatchi.cli run clip.mp4 --live                # report.html + report.html.json
    python -m saatchi.cli serve --live                       # local web UI on :8000
    python -m saatchi.cli mux video.mp4 narration.m4a out.mp4  # attach a recorded narration
    python -m saatchi.cli bench results/ bench/labels.json   # offline scoring, no API calls
See docs/FILMING_GUIDE.md, docs/DEMO_SCRIPT.md, docs/SUBMISSION.md, docs/PUSH_STEPS.md.
