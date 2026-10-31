# Build log (everything below was built during the hackathon, from 26 Oct 2026 21:30 IST)

Rule: no code existed before kickoff. Research notes (no code) were written earlier.
AI-assisted development: this repo was written with Claude Code assistance, directed and reviewed by Kaushik M.

## 2026-10-26
- Re-verified Voice, SAM, Files and Spark-video API shapes against dev.meta.ai docs.
- Skeleton: ingest (ffmpeg), voice client, SAM client + box parser, Spark claim extractor + claim verifier,
  two-channel verifier (abstains on disagreement), bilingual HTML report, CLI with --live guard, 13 unit tests (mocked).

## Not yet verified against the real API
- SAM raw output layout beyond the documented box marker (run `sam-probe`).
- Spark Responses output shape and token cost for video.
- Tamil/Tanglish transcription quality.

## 2026-10-30
- Retries with exponential backoff (429/5xx); Spark-only ablation mode; active re-check loop (`pipeline.recheck`).
- Saatchi-Bench scorer (coverage, accuracy on answered, false-confirmation rate, bootstrap CIs, ablation) - offline.
- Local web UI (stdlib), `mux` helper to attach recorded narrations, docs (filming guide, demo script, submission text, push steps).
- 18 mocked tests pass. Still no live API call made: all [U] items above remain unverified.

## 2026-10-31
- Meta hackathon submission dropped (no payment method for the API). Project continues as a research benchmark on open-weight models.
- Added docs/RESEARCH_PLAN.md after a literature/novelty search (MAD2, TRILOGUE, AVID found; none cover this exact task as far as one search shows).
