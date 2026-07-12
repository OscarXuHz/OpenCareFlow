from __future__ import annotations

import json
import re
from pathlib import Path

from app.config import settings
from app.llm.vision import extract_volunteer_form


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SAMPLE_TEXT = [
    BACKEND_ROOT / "data" / "mock_elder_profile.json",
    BACKEND_ROOT / "data" / "samples" / "visit_note" / "mock_transcript.txt",
    BACKEND_ROOT / "tests" / "visit_note" / "transcript_example.txt",
    BACKEND_ROOT / "app" / "services" / "mock_generator.py",
    BACKEND_ROOT / "app" / "services" / "visit_note_agent" / "mock.py",
    BACKEND_ROOT / "app" / "services" / "welfare_form_extractor.py",
    BACKEND_ROOT / "app" / "llm" / "vision.py",
]

HK_PHONE = re.compile(r"(?<!\d)[2-9]\d{3}[ -]?\d{4}(?!\d)")
HKID = re.compile(r"\b[A-WYZ]\d{6}\([0-9A]\)")


def test_public_sample_text_uses_obviously_invalid_identifiers():
    for path in PUBLIC_SAMPLE_TEXT:
        text = path.read_text(encoding="utf-8")
        assert not HK_PHONE.search(text), f"realistic phone number in {path}"
        assert not HKID.search(text), f"realistic HKID in {path}"


def test_primary_mock_profile_is_marked_synthetic():
    profile = json.loads((BACKEND_ROOT / "data" / "mock_elder_profile.json").read_text())
    assert profile["_synthetic"] is True
    assert profile["phone_mobile"]["full"] == "00000000"
    assert profile["email"].endswith(".invalid")


def test_mock_transcripts_are_marked_synthetic():
    for relative in (
        Path("data/samples/visit_note/mock_transcript.txt"),
        Path("tests/visit_note/transcript_example.txt"),
    ):
        first_line = (BACKEND_ROOT / relative).read_text(encoding="utf-8").splitlines()[0]
        assert "合成資料" in first_line


def test_vision_mock_does_not_return_raw_provider_content(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "llm_provider", "mock")
    monkeypatch.setattr(settings, "store_ai_raw_responses", False)

    result = extract_volunteer_form(tmp_path / "not-read-in-mock.jpg")

    assert "raw" not in result["_meta"]
