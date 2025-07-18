@echo off
rmdir /s /q "./tmp" 
mkdir tmp
findstr /v /c:"find-links" requirements.txt > ./tmp/requirements.txt
pip download --only-binary=:all: --platform manylinux2014_x86_64 --python-version 3.12 --implementation cp -d ./wheels --exists-action i -r ./tmp/requirements.txt 
rmdir /s /q "./tmp" 