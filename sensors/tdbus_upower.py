# -*- coding: utf-8 -*-

'''
This module presents a little code to deal with battery status using DBUS and
UPower on Linux

@author: pkremer
'''

import sys
import logging
from itertools import ifilter
from functools import partial

import tdbus

# 'constants'
UPOWER_NAME = 'org.freedesktop.UPower'
UPOWER_DEVICE_IFACE = 'org.freedesktop.UPower.Device'
UPOWER_PATH = '/org/freedesktop/UPower'
UPOWER_IFACE = 'org.freedesktop.UPower'
DBUS_PROP_NAME = 'org.freedesktop.DBus.Properties'

log = logging.getLogger(__name__)


def convert_DBUS_to_python(val):
    '''
    quick hack to convert DBUS types to python types
    TODO: make this python3 ready
    '''
    if isinstance(val, (str, unicode,)):
        return str(val)
    elif isinstance(val, (int,)):
        return int(val)
    elif isinstance(val, (dict,)):
        return convert_DBUSDictionary_to_dict(val)
    elif isinstance(val, (list,)):
        return convert_DBUSArray_to_tuple(val)
    elif isinstance(val, (tuple,)):
        return val[1]
    elif isinstance(val, (float,)):
        return float(val)
    else:
        raise TypeError("Unknown type '%s': '%r'!" % (str(type(val)),
                                                      repr(val)))


def convert_DBUSArray_to_tuple(dbusarray):
    return ((convert_DBUS_to_python(val) for val in dbusarray),)


def convert_DBUSDictionary_to_dict(dbusdict):
    return {convert_DBUS_to_python(k): convert_DBUS_to_python(dbusdict[k])
                                            for k in dbusdict}


def uPowerEnumerateDevices(conn):
    # list all UPower devices:
    for device in conn.call_method(UPOWER_PATH, member='EnumerateDevices',
                              interface=UPOWER_IFACE,
                              destination=UPOWER_NAME).get_args()[0]:
        yield device


def uPowerDeviceGetAll(conn, device):
    '''
    Utility method that uses the given DBUS connection to call the
    UPower.GetAll method on the UPower device specified and returns pure
    python data.

    :param conn: DBUS connection
    :param device: the device
    '''
    log.debug("uPowerDeviceGetAll %s", device)
    return convert_DBUS_to_python(conn.call_method(device,
                              member='GetAll',
                              interface=DBUS_PROP_NAME,
                              destination=UPOWER_NAME,
                              format='s',
                              args=(UPOWER_DEVICE_IFACE,)
                              ).get_args()[0])


def uPowerDeviceGet(conn, device, attribute):
    log.debug("uPowerDeviceGet %s.%s", device, attribute)
    return convert_DBUS_to_python(
                        conn.call_method(device,
                              member='Get',
                              interface=DBUS_PROP_NAME,
                              destination=UPOWER_NAME,
                              format='ss',
                              args=(UPOWER_DEVICE_IFACE, attribute)
                              ).get_args()[0]
                        )


class UPowerDeviceHandler(tdbus.DBusHandler):
    def __init__(self, connect, devices):
        '''
        A DBUS signal handler class for the org.freedesktop.UPower.Device
        'Changed' event. To re-read the device data, a DBUS connection is
        required. This is established when an event is fired using the provided
        connect method.

        Essentially, this is a cluttered workaround for a bizarre object design
        and use of decorators in the tdbus library.

        :param connect: a DBUS system bus connection factory
        :param devices: the devices to watch
        '''
        self.connect = connect
        self.device_paths = devices
        log.debug('Installing signal handler for devices: %r', devices)
        self._observers = {}
        super(UPowerDeviceHandler, self).__init__()

    def register_observer(self, observer, devices=None):
        """
        register a listener function

        Parameters
        -----------
        observer : external listener function
        events  : tuple or list of relevant events (default=None)
        """
        if devices is not None and type(devices) not in (tuple, list):
            devices = (devices,)

        if observer in self._observers:
            log.warning("Observer '%r' already registered, overwriting for "
                     "devices %r", observer, devices)
        self._observers[observer] = devices

    def notify_observers(self, device=None, attributes=None):
        """notify observers """
        log.debug("%s %r", device, attributes)
        for observer, devices in list(self._observers.items()):
            #log.debug("trying to notify the observer")
            if devices is None or device is None or device in devices:
                try:
                    observer(self, device, attributes)
                except (Exception,) as ex:  # pylint: disable=W0703
                    self.unregister_observer(observer)
                    errmsg = "Exception in message dispatch: Handler '{0}'" + \
                        " unregistered for device '{1}'  ".format(
                                        observer.__class__.__name__, device)
                    log.error(errmsg, exc_info=ex)

    @tdbus.signal_handler(member='Changed', interface=UPOWER_DEVICE_IFACE)
    def Changed(self, message):
        device = message.get_path()
        if device in self.device_paths:
            log.debug('signal received: %s, args = %r', message.get_member(),
                                                  message.get_args())
            conn = self.connect()
            self.notify_observers(device, uPowerDeviceGetAll(conn, device))
            conn.close()


def connect_dbus_system():
    '''
    Factory for DBUS system bus connections
    '''
    return tdbus.SimpleDBusConnection(tdbus.DBUS_BUS_SYSTEM)


def upower_present(connect):
    conn = connect()
    result = conn.call_method(tdbus.DBUS_PATH_DBUS, 'ListNames',
                              tdbus.DBUS_INTERFACE_DBUS,
                              destination=tdbus.DBUS_SERVICE_DBUS)
    conn.close()
    # see if UPower is in the known services:
    return UPOWER_NAME in (name for name in result.get_args()[0]
                            if not name.startswith(':'))


def ibatteries(conn):
    '''
    Utility that returns an generator for rechargeable power devices.

    :param conn: DBUS system bus connection
    '''
    def is_rechargeable(conn, device):
        log.debug("testing IsRechargeable for '%s'", device)
        return uPowerDeviceGet(conn, device, 'IsRechargeable')

    return ifilter(partial(is_rechargeable, conn),
                    uPowerEnumerateDevices(conn))


def main():
    logging.basicConfig(level=logging.DEBUG)

    if not upower_present(connect_dbus_system):
        raise EnvironmentError("DBUS connection to UPower impossible")

    conn = connect_dbus_system()

    conn.add_handler(UPowerDeviceHandler(connect_dbus_system,
                                         set(ibatteries(conn))))
    conn.subscribe_to_signals()

    # basic select() loop, i.e. we assume there is no event loop
    conn.dispatch()

if __name__ == '__main__':
    sys.exit(main())
