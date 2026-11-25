# Build log

Append-only. Read first, written last. One row per session.

| Date | Session | Model | Effort (source) | Minutes | Tiers passed | NOT VERIFIED | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-23 | 7.1 | Sonnet 5.5 (adopted draft: Fable 5.2, 15 Nov 2026) | medium (app session record) | 9 (from the timer hook start 17:07:32Z) | V1-V6 PASS | 4 | https://github.com/ampaduchris/prompts-on-trial/pull/1 |

Notes for 7.1: CI matrix Python 3.11, 3.12, 3.13 on ubuntu-24.04; versions chosen per `STANDARD.md` (minimum 3.11 up to the newest release with wheels for every dependency; there are no runtime dependencies yet). `trace.py` runs in report-only mode (DEV-006).
