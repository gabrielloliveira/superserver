import socket

from server.server import Server


def test_create_super_server():
    """
    Test creating a super server
    """
    server = Server(num_threads=1)

    assert server.host == "127.0.0.1"
    assert server.port == 8080
    assert server.is_subprocess is False
    assert server.num_threads == 1
    assert server.threads == 0
    assert server.sock is not None
    assert server.sock.family == socket.AF_INET
    assert server.sock.type == socket.SOCK_DGRAM
