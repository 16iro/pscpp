@echo off
chcp 65001 > nul
echo [pscpp] 프로젝트 초기 설정을 시작합니다...

:: ── git hook 등록 ────────────────────────────────────────────
git config core.hooksPath .githooks
echo [pscpp] git hooks 등록 완료 (.githooks/)

:: ── .env 생성 (이미 있으면 스킵) ──────────────────────────────
if exist ".env" (
    echo [pscpp] .env 이미 존재합니다. 스킵.
    goto :done
)

:: MSYS2 경로 탐색
set MSYS2_ROOT=C:\msys64
if exist "C:\msys64\usr\bin\bash.exe" set MSYS2_ROOT=C:\msys64
if exist "C:\msys2\usr\bin\bash.exe"  set MSYS2_ROOT=C:\msys2
if not exist "%MSYS2_ROOT%\usr\bin\bash.exe" (
    echo [pscpp] 경고: MSYS2를 찾을 수 없습니다. .env의 MSYS2_ROOT를 직접 수정하세요.
)

:: 컴파일러 감지 (cl.exe 있으면 msvc)
set COMPILER=gcc
where cl.exe >nul 2>&1 && set COMPILER=msvc

:: .env 작성
(
    echo MSYS2_ROOT=%MSYS2_ROOT%
    echo COMPILER=%COMPILER%
) > .env

echo [pscpp] .env 생성 완료
echo         MSYS2_ROOT=%MSYS2_ROOT%
echo         COMPILER=%COMPILER%
echo [pscpp] 경로가 다르다면 .env 를 직접 수정하세요.

:done
echo [pscpp] 설정 완료.
