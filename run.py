# -*- coding: utf-8 -*-

import sys
from threading import Thread


from myapp import socketio, app

from myapp.helpers.upower_socketio import socketio_background_thread
from myapp.views import SIO_SENSOR_NAMESPACE, SIO_EVT_BATTERY_CHANGED

# spawn a background thread and send events via socketio directly to the client
Thread(
        target=socketio_background_thread,
        args=(socketio.emit,
              SIO_EVT_BATTERY_CHANGED,
              SIO_SENSOR_NAMESPACE,)
       ).start()

# allow specifying the IP to listen to, default localhost
if len(sys.argv) > 1:
    socketio.run(app, host=sys.argv[1])
else:
    socketio.run(app)
