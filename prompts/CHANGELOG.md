# Prompt changelog

Each entry explains what changed and why — this is the part of the project
that's actually interesting to show in an interview: prompt engineering is
iterative, and the reasoning behind a change matters as much as the change
itself.

## v1 — initial version

- First version of the system prompt. Defines the exact JSON schema in
  words (kept in sync by hand with `backend/app/schemas.py::AnalysisResult`)
  and gives explicit anti-hallucination instructions for `bullet_rewrites`
  (never invent achievements/metrics not supported by the CV) and for
  `ats_match_score` (score strictly on textual overlap with the JD, not on
  a subjective "feel" of the candidate).
- Explicitly tells the model what to do if the extracted CV text looks
  garbled (common with PDFs that have unusual encoding or multi-column
  layouts) rather than silently guessing.

<!--
When you tweak the prompt: add a new vN_system_prompt.md file (don't edit
v1 in place — keep the history), bump PROMPT_VERSION in
backend/app/prompts.py, and add an entry here describing what changed and,
more importantly, *why* — what failure mode or bad output you were trying
to fix. This file is the artifact: a dated record of prompt iteration.
-->
