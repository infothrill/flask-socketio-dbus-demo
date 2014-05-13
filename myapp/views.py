# -*- coding: utf-8 -*-

from flask import render_template

from . import app, socketio

SIO_SENSOR_NAMESPACE = "/sensors"

SIO_EVT_BATTERY_CHANGED = 'battery_changed'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/battery')
def battery():
    return render_template('battery.html')


@app.route('/battery-dbus')
def battery_dbus():
    return render_template('battery_dbus.html',
                           sio_evt_battery_changed=SIO_EVT_BATTERY_CHANGED,
                           sio_namespace=SIO_SENSOR_NAMESPACE)


@socketio.on('connect', namespace=SIO_SENSOR_NAMESPACE)
def on_connect_sensors():
    app.logger.debug("websocket connect to '%s'", SIO_SENSOR_NAMESPACE)
    from sensors.tdbus_upower import ibatteries, connect_dbus_system, uPowerDeviceGetAll
    conn = connect_dbus_system()
    for bat in ibatteries(conn):
        socketio.emit(SIO_EVT_BATTERY_CHANGED,
                      uPowerDeviceGetAll(conn, bat),
                      namespace=SIO_SENSOR_NAMESPACE)
    conn.close()


@socketio.on('disconnect', namespace=SIO_SENSOR_NAMESPACE)
def on_disconnect_sensors():
    app.logger.debug("websocket disconnect from %s", SIO_SENSOR_NAMESPACE)
