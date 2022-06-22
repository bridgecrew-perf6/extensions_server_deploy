# This script use when run outside docker

kill -15 $(pgrep -f "server.py")
kill -15 $(pgrep -f "discovery.py")
export PATH_TO_HOSTS=/etc/hosts
export PORT=8443
python3 discovery.py 2>&1 &
python3 server.py