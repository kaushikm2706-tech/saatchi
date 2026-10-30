# Filming guide (do this once; ~1-2 hours)

Goal: 3 short clips first (not 12). Measure cost and quality, then film more only if the numbers look sane.

## One clip = one video + three narrations
1. Pick a simple hands-on job with countable objects: fit 4 bolts on a board, plug 3 cables, place 5 coins in a box, arrange 6 books.
2. Film it on your phone, landscape, 30-45 seconds, steady, objects clearly visible, good light. Speak nothing (or keep the phone's original audio; we replace it).
3. Record THREE narrations on your phone's voice recorder, each 15-30 seconds, in Tamil or Tanglish (say the object names in English, like you normally would):
   - truthful: says exactly what you did ("naan 4 bolt fit pannen, appuram ...").
   - false count: same story but a wrong number ("6 bolt fit pannen").
   - false order: same story with steps in the wrong order.
   Write down, for each narration, what you said (needed for the labels file).
4. Copy the video and 3 audio files to the same folder on your laptop.
5. Make 3 test videos (PowerShell, from the project folder; ffmpeg must be installed):
   `python -m saatchi.cli mux c01.mp4 c01_truth.m4a clips/c01_truthful.mp4`
   `python -m saatchi.cli mux c01.mp4 c01_count.m4a clips/c01_false_count.mp4`
   `python -m saatchi.cli mux c01.mp4 c01_order.m4a clips/c01_false_order.mp4`
6. Keep each final file under 50 MB. Do not film other people or private places.

## Cost sanity (from published prices, not a forecast)
SAM: a 45 s clip at 15 fps = 675 frames = about $0.14 per object word. Voice: about $0.002. Spark video cost is UNKNOWN: run ONE clip first and read the `usage` in the response before filming more.

## Labels
Copy `bench/labels.example.json` to `bench/labels.json` and edit: one entry per clip, `match` = a few words from the claim, `gold` = SUPPORTED if the video shows it, CONTRADICTED if not. Only label claims you are sure about.
