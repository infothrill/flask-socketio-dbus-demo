# -*- coding: utf-8 -*-

import sys
from threading import Thread
import logging

from myapp import socketio, app

from myapp.helpers.upower_socketio import socketio_background_thread
from myapp.views import SIO_SENSOR_NAMESPACE, SIO_EVT_BATTERY_CHANGED

_DEFAULT_LOG_FORMAT = '%(asctime)s - %(process)d - %(levelname)s - %(message)s'
LOG = logging.getLogger()

def _configure_logging():
    LOG.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()

    formatter = logging.Formatter(_DEFAULT_LOG_FORMAT)
    ch.setFormatter(formatter)

    LOG.addHandler(ch)

_configure_logging()
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)
try:
    # spawn a background thread and send events via socketio directly to the client
    socketio_thread = Thread(
            target=socketio_background_thread,
            args=(socketio.emit,
                  SIO_EVT_BATTERY_CHANGED,
                  SIO_SENSOR_NAMESPACE,)
           )
    socketio_thread.daemon = True
    socketio_thread.start()
    
    # allow specifying the IP to listen to, default localhost
    if len(sys.argv) > 1:
        socketio.run(app, host=sys.argv[1])
    else:
        socketio.run(app)
except (KeyboardInterrupt, SystemExit):
    print('\n! Received keyboard interrupt, quitting threads.\n')
