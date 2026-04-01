@echo off
chcp 65001 > nul
for /f "usebackq tokens=1,* delims==" %%a in ("%~dp0..\.env") do set %%a=%%b

if "%COMPILER%"=="msvc" (
    set PATH=%MSYS2_ROOT%\usr\bin;%PATH%
) else (
    set PATH=%MSYS2_ROOT%\usr\bin;%MSYS2_ROOT%\mingw64\bin;%PATH%
)

%MSYS2_ROOT%\usr\bin\bash.exe "%~dp0build.sh" %*
