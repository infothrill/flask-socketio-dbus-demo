What is this?
-------------
An demo [Flask](http://flask.pocoo.org/) application that sends
[websocket](http://en.wikipedia.org/wiki/WebSocket)
messages to the browser originating from the Linux
[DBUS](http://www.freedesktop.org/wiki/Software/dbus/),
in this case from the [UPower](http://upower.freedesktop.org/) daemon.
There is only one relevant page in this demo so far, which shows the
battery status of the host it is run on.

This only works on Linux, and was tested and developed on Ubuntu 13.10

Installation on Ubuntu
----------------------

    # apt-get install python-virtualenv
    # virtualenv venv
    # source venv/bin/activate
    # pip install -r requirements.txt

Running it
----------
Start the webservice:
 
    # python run.py

Challenges encountered
----------------------
- python-dbus doesn't work for this, because it can't be run in a subthread
  while still using its mainloop
- virtualenv/pip is required because:
	- Flask-SocketIO not available in ubuntu 13.10
	- python-tdbus not available in ubuntu 13.10


Useful links and further reading
--------------------------------
https://pypi.python.org/pypi/python-tdbus
http://upower.freedesktop.org/

Linux Journal article on DBUS:
http://www.linuxjournal.com/article/10455?page=0,0

