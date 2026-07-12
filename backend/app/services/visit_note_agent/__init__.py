"""visit_note_agent — 家訪語音轉結構化報告 sub-package.

Originally authored by partner branch (`branch/CareFlow/visit_note_agent/`).
Adapted to:
  - Unified Bailian OpenAI-compatible client (no requests / OpenRouter direct).
  - Bailian fun-asr instead of Google Cloud Speech-to-Text.
  - Two-phase flow (extract → human review → render) to satisfy the
    CareFlow mandatory-review rule.
  - Encrypted transcript vault (no plaintext on disk).
"""
from __future__ import annotations

from .service import generate_visit_case_note, run_extraction, run_render

__all__ = ["generate_visit_case_note", "run_extraction", "run_render"]
