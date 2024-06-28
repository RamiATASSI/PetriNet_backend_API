from flask_socketio import SocketIO
from flask_apscheduler import APScheduler

socketio = SocketIO(async_mode='gevent', cors_allowed_origins="*")
scheduler = APScheduler()
