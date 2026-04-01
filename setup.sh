#!/usr/bin/env bash
# macOS / Linux 초기 설정

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "[pscpp] 프로젝트 초기 설정을 시작합니다..."

# git hook 등록
git -C "$ROOT" config core.hooksPath .githooks
chmod +x "$ROOT/.githooks/post-checkout"
echo "[pscpp] git hooks 등록 완료 (.githooks/)"

# .env (macOS/Linux 는 .bat 미사용이므로 최소 생성)
if [[ -f "$ROOT/.env" ]]; then
    echo "[pscpp] .env 이미 존재합니다. 스킵."
else
    cp "$ROOT/.env.example" "$ROOT/.env"
    echo "[pscpp] .env 생성 완료 (.env.example 복사)"
fi

echo "[pscpp] 설정 완료."
