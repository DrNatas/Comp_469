# MEMORY.md - COMP 469 Course State

Last verified: 2026-08-13

## Content Inventory (source of truth — verify against disk before trusting)

Course materials live in `../Fall 2026/` (sibling to this `openclaw/`
workspace), not inside `openclaw/` itself:

- `L01`–`L15` + `Advanced Topics/` — full lecture set: slides (.pptx),
  speaker notes (.docx), and Berkeley CS188 slides/transcripts used as
  supplementary base material. Folder names carry AIMA 4th ed. chapter.section
  mappings.
- `Assessments/` — Canvas quiz `.adoc` sources + QTI exports for weeks
  **1, 2, 3, 4, 5, 6, 7, and 15 only**. Weeks 8–14 have no quiz yet.
- `Projects/search/` — full Berkeley Pacman search project (autograder,
  solutions walkthrough, instructor notes) — complete.
- `Reading/` — AsciiDoc textbook build (`textbook.adoc` / `.html`) plus a
  reference PDF — complete.
- `openclaw/Labs/GenerativePreTraining/` — the only lab built inside this
  workspace: a GPT-paper-replication assignment (README, instructor +
  checklist docs, 6 notebooks, `src/`).

`COMP469_Syllabus.adoc` and `COMP469_Lab_Guide_Fall2026.adoc` (previously
referenced in AGENTS.md) do **not exist anywhere in the repo**. Do not assume
they exist until someone creates them.

## Known Gaps / TODOs

- Quizzes missing for weeks 8–14 in `Assessments/`.
- `L9 - RL I - 5.1 to 5.3` — verify this chapter/section label against AIMA
  4th ed.'s actual Reinforcement Learning chapter before citing it; the
  range looks inconsistent with the rest of the AIMA-mapped folder names and
  may have been copied from CS188 lecture numbering instead.
- No syllabus or lab guide document exists yet, despite being referenced
  historically — flag rather than fabricate one if asked to "update" it.

## Recent Decisions

- 2026-08-13: Rebuilt this file (was corrupted — contained leftover
  OCR/transcription filler text instead of real memory). Rebuilt AGENTS.md,
  SOUL.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md to reflect actual repo state
  and to bake in citation/accuracy rigor as standing behavior. Removed a
  duplicate `openclaw-workspace-state.json` (canonical copy stays at
  `.openclaw/workspace-state.json`).
