@echo off
setlocal enabledelayedexpansion

echo Changing directory to "%CD%"
cd  /D "%~dp0"

echo Activating virtual environment
call .venv\Scripts\activate

echo Running ollama serve
ollama serve

echo Running open-webui serve
for /f "tokens=*" %%A in ('open-webui serve') do (
    set OUTPUT=%%A
    if "!OUTPUT:INFO:     Application startup complete.=!" neq "!OUTPUT!" start  "" "http://127.0.0.1:8080"
)

echo Opening web browser on http://127.0.0.1:8080
endlocal

