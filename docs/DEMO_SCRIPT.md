# 3-minute demo script (record screen + voice; keep under 3:00)

0:00-0:20  Problem. "In Chennai, contractors and technicians report work by WhatsApp voice notes in Tamil. Nobody can check them. Saatchi checks what is said against what the video shows."
0:20-0:40  Show the repo and BUILD_LOG.md and `git log` (first commit date 26 Oct 2026) so judges see this was built during the event.
0:40-1:30  Live run on a TRUTHFUL clip: upload in the web UI, show Tamil transcript turns, extracted claims, SAM overlay/track count, verdicts SUPPORTED with timestamps.
1:30-2:15  Same video, FALSE narration ("6 bolts"). Show the channels disagreeing and Saatchi refusing to confirm, with the Tamil+English request for proof.
2:15-2:40  The loop: send the requested clip, claim re-verified.
2:40-3:00  Numbers from `python -m saatchi.cli bench ...`: false-confirmation rate, Spark-only vs Spark+SAM, with the confidence intervals and the small-sample warning. State limits honestly.

Rules: show only what was built in the event; do not use fabricated numbers; if something failed in a run, say so.
Record twice, keep the better take. Upload unlisted to YouTube; test the link logged out.
