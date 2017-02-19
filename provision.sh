#!/bin/bash

apt-get update
apt-get install -y python python-dev python-virtualenv python3 python3-dev
apt-get install -y pkg-config libdbus-1-dev upower pm-utils
apt-get install -y git

# not needed on systemd based systems:
# /etc/init.d/dbus start

# make sure upower is started:
upower -e

echo "Please create a virtualenv, install requirements and execute run.py 0.0.0.0"
