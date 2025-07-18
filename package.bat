@echo off
for %%i in ("%CD%") do set "dir_name=%%~nxi"

for /f "tokens=2 delims=: " %%a in ('findstr /r /c:"^version: *" "./manifest.yaml"') do (
    set version=%%a
)
echo packing plugin version %version%
dify plugin package ./ -o ./target/%dir_name%_%version%.difypkg
echo packing finish