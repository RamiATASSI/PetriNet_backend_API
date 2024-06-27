from flask import Flask
from .events import socketio, scheduler
from .routes import main



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "secret"
    app.config['DEBUG'] = False

    app.register_blueprint(main)

    socketio.init_app(app)
    # scheduler.init_app(app)
    scheduler.start()

    return app
