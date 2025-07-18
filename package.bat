@echo off
for %%i in ("%CD%") do set "dir_name=%%~nxi"
echo %dir_name%

dify plugin package ./ -o ./target/%dir_name%.difypkg