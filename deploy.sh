#!/bin/bash

rsync -av --exclude=extensions_server.db --exclude=venv --exclude=dist --exclude=__pycache__ --exclude=.*  ./* ../extensions_server_deploy/
pyarmor obfuscate --platform linux.aarch64 server.py
cp -r ./dist/* ../extensions_server_deploy
cd ../extensions_server_deploy
git add .
git commit -m 'update'
git push origin master