# This script use when run outside docker

kill -15 $(pgrep -f "server.py")
kill -15 $(pgrep -f "discovery.py")
export PATH_TO_HOSTS=/etc/hosts
export PORT=8443
python discovery.py 2>&1 &
python server.py