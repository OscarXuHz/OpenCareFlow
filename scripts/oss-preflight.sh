#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

failed=0

report() {
  printf 'ERROR: %s\n' "$1" >&2
  failed=1
}

forbidden_path_re='(^|/)(\.env(\..*)?|\.htpasswd[^/]*|careflow\.db([^/]*)?|\.transcript_key|proof_of_AI_use\.zip)$|(^|/)(uploads|exports|transcripts|visit_sessions|welfare_outputs|theta_pdfs|logs)/'

while IFS= read -r path; do
  [ -e "$path" ] || continue
  case "$path" in
    .env.example|backend/.env.example|*.env.example|*.env.example.*)
      continue
      ;;
  esac
  if printf '%s\n' "$path" | grep -Eq "$forbidden_path_re"; then
    report "forbidden public path: $path"
  fi
done < <(git ls-files --cached --others --exclude-standard)

if ! command -v python3 >/dev/null 2>&1; then
  report "python3 is required for secret and PII scanning"
elif ! python3 - <<'PY'
import re
import subprocess
import sys
from pathlib import Path

SECRET = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    r"|\b(?:sk|hf)_[A-Za-z0-9_-]{16,}"
    r"|\bsk-[A-Za-z0-9_-]{16,}"
)
HK_PHONE = re.compile(r"(?<!\d)[2-9]\d{3}[ -]?\d{4}(?!\d)")
HKID = re.compile(r"\b[A-WYZ]\d{6}\([0-9A]\)")
PII_SCOPE = {
  "backend/data/mock_elder_profile.json",
  "backend/tests/visit_note/transcript_example.txt",
  "backend/app/services/mock_generator.py",
  "backend/app/services/visit_note_agent/mock.py",
  "backend/app/services/welfare_form_extractor.py",
  "backend/app/llm/vision.py",
}

raw_paths = subprocess.run(
    ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
    check=True,
    stdout=subprocess.PIPE,
).stdout.split(b"\0")

failed = False
for raw_path in raw_paths:
    if not raw_path:
        continue

    path = Path(raw_path.decode("utf-8", errors="surrogateescape"))
    if not path.is_file() or path.suffix == ".lock" or ".private" in path.parts:
        continue

    data = path.read_bytes()
    if b"\0" in data[:8192]:
        continue
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        continue

    if SECRET.search(text):
        print(f"ERROR: possible secret material: {path}", file=sys.stderr)
        failed = True
    is_sample = (
      path.as_posix() in PII_SCOPE
      or path.as_posix().startswith("backend/data/samples/visit_note/")
    )
    if is_sample and (HK_PHONE.search(text) or HKID.search(text)):
        print(f"ERROR: realistic Hong Kong phone number or HKID: {path}", file=sys.stderr)
        failed = True

sys.exit(1 if failed else 0)
PY
then
  failed=1
fi

if [ "$failed" -ne 0 ]; then
  exit 1
fi

printf 'Open-source current-tree preflight passed.\n'
