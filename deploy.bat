@echo off
"%~dp0.venv\Scripts\reflex.exe" deploy --no-interactive --exclude-from-backend assets --exclude-from-backend .photoshop_sources --exclude-from-backend .scratch %*

