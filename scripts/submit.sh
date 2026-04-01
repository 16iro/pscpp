#!/usr/bin/env bash
# 테스트 통과 후 커밋 (제출 직전 스냅샷)
# 사용법: ./scripts/submit.sh <플랫폼> <문제번호> ["커밋 메시지 suffix"]
# 예시:   ./scripts/submit.sh BOJ 1000 "fix off-by-one"

set -euo pipefail

PLATFORM="${1:-}"
PROB="${2:-}"
MSG="${3:-}"

if [[ -z "$PLATFORM" || -z "$PROB" ]]; then
    echo "Usage: $0 <platform> <problem_number> [message]"
    exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROB_DIR="$PLATFORM/$PROB"

# 해당 문제 폴더에 변경사항이 있는지 확인
if git -C "$ROOT" diff --quiet HEAD -- "$PROB_DIR" && \
   git -C "$ROOT" diff --quiet --cached HEAD -- "$PROB_DIR"; then
    echo "No changes in $PROB_DIR"
    exit 0
fi

# attempt 번호 계산 (해당 문제의 커밋 수 + 1)
ATTEMPT=$(git -C "$ROOT" log --oneline -- "$PROB_DIR" 2>/dev/null | wc -l)
ATTEMPT=$(( ATTEMPT + 1 ))

# 커밋 메시지 조합
if [[ -n "$MSG" ]]; then
    COMMIT_MSG="${PLATFORM}/${PROB}: attempt #${ATTEMPT} - ${MSG}"
else
    COMMIT_MSG="${PLATFORM}/${PROB}: attempt #${ATTEMPT}"
fi

# 스테이징 및 커밋 (main.cpp, README.md, input.txt, expected.txt 만)
git -C "$ROOT" add \
    "$PROB_DIR/main.cpp" \
    "$PROB_DIR/README.md" \
    "$PROB_DIR/input.txt" \
    "$PROB_DIR/expected.txt" \
    2>/dev/null || true

git -C "$ROOT" commit -m "$COMMIT_MSG"

echo ""
echo "Committed: $COMMIT_MSG"
echo "→ Now submit to $PLATFORM manually."
