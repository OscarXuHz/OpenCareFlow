#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

failed=0
secret_paths="$(mktemp)"
trap 'rm -f "$secret_paths"' EXIT

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

if rg --hidden -l -g '!.git/**' -g '!.private/**' -g '!*.lock' '(-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(sk|hf)_[A-Za-z0-9_-]{16,}|\bsk-[A-Za-z0-9_-]{16,})' . >"$secret_paths"; then
  while IFS= read -r path; do
    report "possible secret material: $path"
  done <"$secret_paths"
fi

if rg --pcre2 -n '(?<![0-9])[2-9][0-9]{3}[ -]?[0-9]{4}(?![0-9])|\b[A-WYZ][0-9]{6}\([0-9A]\)' backend/data/mock_elder_profile.json backend/data/samples/visit_note backend/tests/visit_note/transcript_example.txt backend/app/services/mock_generator.py backend/app/services/visit_note_agent/mock.py backend/app/services/welfare_form_extractor.py backend/app/llm/vision.py; then
  report "public sample contains a realistic phone number or HKID"
fi

if [ "$failed" -ne 0 ]; then
  exit 1
fi

printf 'Open-source current-tree preflight passed.\n'
