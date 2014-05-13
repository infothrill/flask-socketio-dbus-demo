# -*- coding: utf-8 -*-

'''
This module provides the glue between our main flask run program and the 
sensors.tdbus_upower module, i.e. it exposes a minimal interface for
starting an event loop to watch for battery events given only the function to
emit websocket messages for the browser.

@author: pkremer
'''

import logging

from sensors.tdbus_upower import upower_present, connect_dbus_system, UPowerDeviceHandler, ibatteries

log = logging.getLogger(__name__)


def socketio_notify(socketio_emit, socketio_event, socketio_namespace, sender, device, attributes):
    log.debug("socketio_notify %r %r %r %r", socketio_event, sender, device, attributes)
    socketio_emit(socketio_event, attributes, namespace=socketio_namespace)


def socketio_background_thread(socketio_emit, socketio_event, namespace):
    log.debug("Starting upower dispatcher loop for socketio namespace %s", namespace)
    if not upower_present(connect_dbus_system):
        raise EnvironmentError("UPower not present on DBUS")

    conn = connect_dbus_system()
    hndlr = UPowerDeviceHandler(connect_dbus_system, set(ibatteries(conn)))
    from functools import partial
    notify = partial(socketio_notify, socketio_emit, socketio_event, namespace)
    hndlr.register_observer(notify, devices=None)
    conn.add_handler(hndlr)
    conn.subscribe_to_signals()
    # basic select() loop, i.e. we assume there is no event loop
    conn.dispatch()
