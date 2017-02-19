## What is this?

An demo [Flask](http://flask.pocoo.org/) application that sends
[websocket](http://en.wikipedia.org/wiki/WebSocket)
messages to the browser originating from the Linux
[DBUS](http://www.freedesktop.org/wiki/Software/dbus/),
in this case from the [UPower](http://upower.freedesktop.org/) daemon.
There is only one relevant page in this demo so far, which shows the
battery status of the host it is run on.

This only works on Linux, was originally developed on Ubuntu 13.10, but also works on Ubuntu 16.04.

## Installation on Ubuntu

See `provision.sh` for basic python and system dependencies.

```sh
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

A sample `Vagrantfile` is provided to get started on Ubuntu 16.04.

## Running it

Start the webservice:

```sh 
python run.py 0.0.0.0
```

## Requirements

* DBUS
* python2.7+ or python3.5+ (not sure about the versions in between, I never tried)

## Challenges encountered

- python-dbus didn't work for this, because it can't be run in a subthread
  while still using its main loop

## Useful links and further reading

https://pypi.python.org/pypi/python-tdbus

http://upower.freedesktop.org/

Linux Journal article on DBUS:
http://www.linuxjournal.com/article/10455?page=0,0

