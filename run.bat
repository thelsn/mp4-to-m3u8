@echo off
setlocal enabledelayedexpansion

:: Check if ffmpeg is installed
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo ffmpeg is not installed.
    exit /b 1
)

:: Validate input
if "%~1"=="" (
    echo Usage: %~nx0 input-filename.mp4
    exit /b 1
)

set "input_file=%~1"
set "directory=%~n1"

if not exist "%input_file%" (
    echo Input file does not exist.
    exit /b 1
)

:: Create directory
if not exist "%directory%" mkdir "%directory%"

echo Converting "%input_file%" to HLS format...

:: Get duration of the video
for /f "tokens=2 delims=, " %%a in ('ffmpeg -i "%input_file%" 2^>^&1 ^| find "Duration"') do set "duration=%%a"
for /f "tokens=1-3 delims=:" %%a in ("!duration!") do (
    set /a total_seconds=%%a*3600 + %%b*60 + %%c
)

:: Run ffmpeg and track progress
ffmpeg -i "%input_file%" -c:v libx264 -c:a aac -hls_time 3 -hls_list_size 0 -hls_segment_filename "%directory%\%directory%-segment_%%03d.ts" "%directory%\%~n1.m3u8" 2^>^&1 | findstr /r "time=[0-9][0-9]:[0-9][0-9]:[0-9][0-9]" > progress.log & (
    for /f "tokens=2 delims== " %%t in ('type progress.log') do (
        for /f "tokens=1-3 delims=:" %%a in ("%%t") do (
            set /a current_seconds=%%a*3600 + %%b*60 + %%c
            set /a percent=!current_seconds!*100/!total_seconds!
            <nul set /p="["
            for /l %%i in (1,1,!percent!) do <nul set /p="="
            for /l %%i in (!percent!,1,100) do <nul set /p=" "
            echo ] !percent!%%
        )
    )
)

echo.
echo Conversion Complete!
exit /b 0
