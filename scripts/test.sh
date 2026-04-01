#!/usr/bin/env bash
# 빌드 후 input.txt 실행 결과를 expected.txt 와 diff
# 사용법: ./scripts/test.sh <플랫폼> <문제번호>
# 예시:   ./scripts/test.sh BOJ 1000

set -euo pipefail

PLATFORM="${1:-}"
PROB="${2:-}"

if [[ -z "$PLATFORM" || -z "$PROB" ]]; then
    echo "Usage: $0 <platform> <problem_number>"
    exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
PROB_DIR="$ROOT/$PLATFORM/$PROB"
BIN="$BUILD/$PLATFORM/$PROB/${PLATFORM}_${PROB}"

# Windows(Git Bash) 에서는 .exe 붙음
[[ -f "${BIN}.exe" ]] && BIN="${BIN}.exe"

# 빌드
cmake -S "$ROOT" -B "$BUILD" -DCMAKE_BUILD_TYPE=Release > /dev/null 2>&1
cmake --build "$BUILD" --target "${PLATFORM}_${PROB}" -- -j4

if [[ ! -f "$BIN" ]]; then
    echo "Binary not found: $BIN"
    exit 1
fi

if [[ ! -s "$PROB_DIR/input.txt" ]]; then
    echo "input.txt is empty — skipping test"
    exit 0
fi

ACTUAL=$("$BIN" < "$PROB_DIR/input.txt")
EXPECTED=$(cat "$PROB_DIR/expected.txt")

if diff <(echo "$ACTUAL") <(echo "$EXPECTED") > /dev/null 2>&1; then
    echo "✓ PASS — BOJ/$PROB"
else
    echo "✗ FAIL — BOJ/$PROB"
    echo "--- expected"
    echo "$EXPECTED"
    echo "+++ actual"
    echo "$ACTUAL"
    exit 1
fi
