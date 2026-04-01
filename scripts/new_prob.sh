#!/usr/bin/env bash
# 사용법: ./scripts/new_prob.sh <플랫폼> <문제번호>
# 예시:   ./scripts/new_prob.sh BOJ 1000

set -euo pipefail

PLATFORM="${1:-}"
PROB="${2:-}"

if [[ -z "$PLATFORM" || -z "$PROB" ]]; then
    echo "Usage: $0 <platform> <problem_number>"
    echo "  e.g. $0 BOJ 1000"
    exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/$PLATFORM/$PROB"

if [[ -d "$DEST" ]]; then
    echo "Already exists: $DEST"
    exit 1
fi

mkdir -p "$DEST"

# main.cpp — 템플릿 복사
cp "$ROOT/templates/template.cpp" "$DEST/main.cpp"

# README.md — 번호 치환
sed "s/{번호}/$PROB/g" "$ROOT/templates/template.md" > "$DEST/README.md"

# 빈 테스트 파일
touch "$DEST/input.txt" "$DEST/expected.txt"

echo "Created: $DEST"
echo "  main.cpp / README.md / input.txt / expected.txt"
