from flask_socketio import SocketIO
from flask_apscheduler import APScheduler

socketio = SocketIO(cors_allowed_origins="*")
scheduler = APScheduler()
