# This script use when run outside docker
cd /root/extensions_server_deploy
echo "$PWD"

kill -15 $(pgrep -f "server.py")
kill -15 $(pgrep -f "discovery.py")
export PATH_TO_HOSTS=/etc/hosts
export PORT=8443
venv/bin/python3.8 discovery.py 2>&1 &
venv/bin/python3.8 server.py