#!/usr/bin/env bash
# 특정 문제만 컴파일
# 사용법: ./scripts/build.sh <플랫폼> <문제번호>
# 예시:   ./scripts/build.sh BOJ 1000

set -euo pipefail

PLATFORM="${1:-}"
PROB="${2:-}"

if [[ -z "$PLATFORM" || -z "$PROB" ]]; then
    echo "Usage: $0 <platform> <problem_number>"
    exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"

if [[ "${COMPILER:-gcc}" == "msvc" ]]; then
    cmake -S "$ROOT" -B "$BUILD" > /dev/null 2>&1
    cmake --build "$BUILD" --target "${PLATFORM}_${PROB}" --config Release
else
    cmake -S "$ROOT" -B "$BUILD" -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release > /dev/null 2>&1
    cmake --build "$BUILD" --target "${PLATFORM}_${PROB}" -- -j4
fi

BIN="$BUILD/$PLATFORM/$PROB/${PLATFORM}_${PROB}"
[[ -f "${BIN}.exe" ]] && BIN="${BIN}.exe"

echo "빌드 완료: $BIN"
