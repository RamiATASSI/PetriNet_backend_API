import unittest
from src.Flask_API.app import app

import pytest
from flask_testing import TestCase
from websocket import create_connection

class TestFlaskRoutes(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_index(self):
        response = self.client.get('/')
        self.assert200(response)

@pytest.fixture(scope="module")
def socket_connection():
    ws = create_connection("ws://localhost:5000")
    yield ws
    ws.close()

def test_socket_connection(socket_connection):
    socket_connection.send("connect")
    result = socket_connection.recv()
    assert result == "User connected"

    socket_connection.send("disconnect")
    result = socket_connection.recv()
    assert result == "User disconnected"

if __name__ == '__main__':
    unittest.main()
