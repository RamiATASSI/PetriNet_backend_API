from src.Flask_API import create_app, socketio

app = create_app()


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
