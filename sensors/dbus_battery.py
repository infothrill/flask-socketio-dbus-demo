# -*- coding: utf-8 -*-

"""
This module has some functionality to interact with the system DBUS and UPower
to find information about power devices. It should be noted that this module
is not used within the bigger scope of this flask application, since it turns
out that dbus-python depends on glib and ships a non thread safe main loop only
which also seems to interfere with greenlets from Flask-SocketIO.

For an implementation that seems to work with Flask-SocketIO, see tdbus_upower
"""

import dbus

# import gobject
# gobject.threads_init()
# dbus.mainloop.glib.threads_init()

_EVENT_BATTERY_CHANGED = 'battery_changed'

UP_NAME = 'org.freedesktop.UPower'
UP_PATH = '/org/freedesktop/UPower'
DEV_NAME = UP_NAME + '.Device'
DB_PROP_NAME = 'org.freedesktop.DBus.Properties'


class Battery(object):
    """
    A little helper class to query battery status and react to changes
    given a valid DBUS system bus connection and device representation.
    """
    def __init__(self, sysbus, device):
        self.sysbus = sysbus
        self.device = device
        self.socketio = None

    def setup_socketio(self, socketio, event, namespace):
        self.socketio = socketio
        self.socketio_event = event
        self.socketio_namespace = namespace

    def changed(self):
        if self.socketio:
            result = self.query()
            self.socketio.emit(self.socketio_event, result, self.socketio_namespace)
        else:
            result = self.query()
            # for terminal demo purposes:
            print result
            return result

    def query(self):
        properties = ('TimeToFull', 'TimeToEmpty', 'Percentage')
        dev_proxy = self.sysbus.get_object(UP_NAME, self.device)
        dev_prop_iface = dbus.Interface(dev_proxy, DB_PROP_NAME)
        result = {}
        for prop in properties:
            result[prop] = dev_prop_iface.Get(DEV_NAME, prop)
        return result


def _find_battery_device(sysbus, up_iface):
    for dev in up_iface.EnumerateDevices():
        dev_proxy = sysbus.get_object(UP_NAME, dev)
        dev_prop_iface = dbus.Interface(dev_proxy, DB_PROP_NAME)
        if (dev_prop_iface.Get(DEV_NAME, 'IsRechargeable')):
            # print "Found a rechargeable battery!"
            return dev
    return None


def mainloop(socketio=None, sio_event=None, sio_namespace=None):
    import gobject
    import dbus.mainloop.glib


    # gobject.threads_init()
    # dbus.mainloop.glib.threads_init()

    # Set up main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Register ourselves as a service
    sysbus = dbus.SystemBus()
    up_proxy = sysbus.get_object(UP_NAME, UP_PATH)
    up_iface = dbus.Interface(up_proxy, UP_NAME)

    thebatterydev = _find_battery_device(sysbus, up_iface)
    if not thebatterydev:
        raise RuntimeError('Error: No usable battery device found')

    bat = Battery(sysbus, thebatterydev)
    if socketio is not None:
        bat.setup_socketio(socketio, sio_event, sio_namespace)
        # print "Setup socketio done"
    # print bat.query()

    # establish a main loop for catching events realting to battery state changes
    dev_proxy = sysbus.get_object(UP_NAME, thebatterydev)
    dev_proxy.connect_to_signal('Changed', bat.changed, dbus_interface='org.freedesktop.UPower.Device')

    # Go!
    loop = gobject.MainLoop()
    loop.run()


def background_thread(socketio, sio_namespace):
    """Watches DBUS for battery status changes and sends socketio events."""
    mainloop(socketio=socketio, sio_event=_EVENT_BATTERY_CHANGED, sio_namespace=sio_namespace)

if __name__ == '__main__':
    # this will install a signal handler for battery changes and dump some
    # battery related information when these events occur
    mainloop()
