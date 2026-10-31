# Saatchi-Bench: research plan (draft, 31 Oct 2026)

## Question
When a person narrates what they did in Tamil, Tanglish or English, can open-weight speech + video models tell
truthful claims from falsified ones, and how often do they wrongly confirm a falsified claim?
Primary metric: **false-confirmation rate** (falsified claim marked SUPPORTED), with abstention (UNVERIFIABLE) allowed.

## Where it sits (searched 31 Oct 2026; one search session, so absence of prior work is NOT proven)
- Spoken-claim verification exists for audio/text only: MAD2 (English, 3,368 claims, no video), TRILOGUE (English/Russian/Kazakh, text evidence, no Tamil).
- AVID (arXiv 2604.13593) tests audio-visual inconsistency in video, but inconsistencies are synthetic audio edits and the paper does not check spoken claims against specific physical actions (counts, order); languages unspecified.
- Not found in that search: a benchmark of real self-filmed narrated actions with falsified counts/order/state in Tamil/Tanglish.
Before writing any paper, repeat the search (Google Scholar, arXiv, ACL Anthology) with more query variants.

## Design
- Claim types: count, order, state, tool/object.
- Each filmed video gets: 1 truthful narration + falsified narrations (wrong count, wrong order, wrong state). Same video, different audio, so the visual evidence is held fixed.
- Language is a variable: Tamil, Tanglish, English narrations of the same facts.
- Systems (all open-weight, free): Whisper for speech; a Qwen3-VL (Apache-2.0; sizes 2B/4B/8B/32B) for video reasoning; optionally an open object tracker for the second channel (check which SAM-family weights are open before promising this). Agreement/abstention rule as in saatchi/verifier.py.
- Controls: (1) gold transcript vs ASR transcript, to separate ASR errors from verification errors; (2) video-blind baseline (text only) to show the video matters; (3) Spark-only style ablation = single channel vs two channels.
- Statistics: bootstrap 95% CIs (already in saatchi/bench.py). Rough guide: worst-case binomial CI is about +/-10 points at n=100 claims per condition, so target >=100 claims per condition before claiming differences.
- Ethics: film only yourself/your own objects, no private places or other people.

## Compute (laptop has no GPU)
Run Whisper and Qwen3-VL in a free GPU notebook (Kaggle or Colab). Current free-GPU quotas are NOT verified here; check the provider pages. Start with small models (Qwen3-VL 2B/4B) and fewer frames per video.

## Known facts to cite carefully
- Whisper-medium fine-tuned on Kathbath Tamil: WER 23.85 baseline (arXiv 2606.09535); this is a fine-tuned figure, not zero-shot, and not Tanglish.
- Qwen3-VL advertises timestamp-grounded event localization; its real accuracy on our clips is unmeasured.

## Milestones
1. Open-model backends behind the same interfaces (Voice -> Whisper, Spark -> Qwen3-VL) + mocked tests.
2. Film 10 videos x (1 truthful + 3 false) x 2 languages, label every claim.
3. Run, score with `saatchi bench`, inspect failures by hand.
4. Write up with limitations; repeat the literature search first.
