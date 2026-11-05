@echo off
if /I "%~1"=="deploy" (
    shift
    "%~dp0.venv\Scripts\reflex.exe" deploy --exclude-from-backend assets --exclude-from-backend .photoshop_sources --exclude-from-backend .scratch %1 %2 %3 %4 %5 %6 %7 %8 %9
) else (
    "%~dp0.venv\Scripts\reflex.exe" %*
)
