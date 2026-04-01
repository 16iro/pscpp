#!/usr/bin/env bash
# 빌드 후 input.txt / expected.txt (<<<PSCPP>>> 구분) 로 diff 검증
# 사용법: ./scripts/test.sh <플랫폼> <문제번호>

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
SEP="<<<PSCPP>>>"

[[ -f "${BIN}.exe" ]] && BIN="${BIN}.exe"

# ── 빌드 ──────────────────────────────────────────────────────
if [[ "${COMPILER:-gcc}" == "msvc" ]]; then
    cmake -S "$ROOT" -B "$BUILD" > /dev/null 2>&1
    cmake --build "$BUILD" --target "${PLATFORM}_${PROB}" --config Release
else
    cmake -S "$ROOT" -B "$BUILD" -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release > /dev/null 2>&1
    cmake --build "$BUILD" --target "${PLATFORM}_${PROB}" -- -j4
fi

[[ -f "$BIN" ]] || { echo "Binary not found: $BIN"; exit 1; }

# ── SEP 기준으로 파일을 케이스 배열로 분리 ────────────────────
split_cases() {
    local file="$1"
    local -n _out="$2"
    _out=()
    local block=""
    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ "$line" == "$SEP" ]]; then
            _out+=("$block")
            block=""
        else
            block+="${block:+$'\n'}$line"
        fi
    done < "$file"
    # 마지막 블록 (trailing newline 만 있으면 빈 케이스로 처리)
    _out+=("$block")
}

# ── 테스트 파일 존재 확인 ─────────────────────────────────────
if [[ ! -f "$PROB_DIR/input.txt" || ! -s "$PROB_DIR/input.txt" ]]; then
    echo "input.txt 없거나 비어있음 — 스킵"
    exit 0
fi

split_cases "$PROB_DIR/input.txt"    INPUTS
split_cases "$PROB_DIR/expected.txt" EXPECTS

N_IN=${#INPUTS[@]}
N_EX=${#EXPECTS[@]}
N_RUN=$(( N_IN < N_EX ? N_IN : N_EX ))   # min

if (( N_IN != N_EX )); then
    echo "⚠ 케이스 수 불일치 — input: ${N_IN}개, expected: ${N_EX}개 → ${N_RUN}개만 테스트"
fi

# ── 케이스별 실행 ─────────────────────────────────────────────
PASS=0; FAIL=0

for (( i=0; i<N_RUN; i++ )); do
    INPUT="${INPUTS[$i]}"
    EXPECT="${EXPECTS[$i]}"
    CASE_NUM=$(( i + 1 ))

    # 빈 케이스 스킵
    if [[ -z "${INPUT//[$'\n\r\t ']/}" ]]; then
        echo "⚠ SKIP [케이스 ${CASE_NUM}] — 빈 입력"
        continue
    fi

    ACTUAL=$(echo "$INPUT" | "$BIN")

    if diff <(echo "$ACTUAL") <(echo "$EXPECT") > /dev/null 2>&1; then
        echo "✓ PASS [케이스 ${CASE_NUM}]"
        ((PASS++)) || true
    else
        echo "✗ FAIL [케이스 ${CASE_NUM}]"
        diff <(echo "$ACTUAL") <(echo "$EXPECT") || true
        ((FAIL++)) || true
    fi
done

echo ""
echo "결과: ${PASS} passed, ${FAIL} failed — $PLATFORM/$PROB"
[[ $FAIL -eq 0 ]]
