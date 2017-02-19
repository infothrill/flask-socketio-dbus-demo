# -*- coding: utf-8 -*-

"""
Pretty boiler plate flask setup with Flask-SocketIO
"""

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app)

#from . import views
