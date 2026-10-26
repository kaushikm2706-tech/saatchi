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
