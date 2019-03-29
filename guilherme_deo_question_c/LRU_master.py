import socket
import time
import importlib
import sqlite3

cache_dll_module = importlib.import_module('CacheDoubleLinkedList')
CacheDLL = getattr(cache_dll_module, 'CacheDoubleLinkedList')
DLLNode = getattr(cache_dll_module, 'Node')


def listen_for_calls(connection):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8741))

    server_socket.listen(5)
    while True:
        print("Running Master...")

        client_socket, address = server_socket.accept()
        data = client_socket.recv(1024)
        data = data.decode()
        print("Received request: {}".format(data))

        data = get_from_db(connection, data)
        client_socket.sendall(data.encode())
        client_socket.close()


def get_from_db(connection, data):
    c = connection.cursor()
    c.execute('SELECT * FROM users WHERE name="{}"'.format(data))
    return str(c.fetchall())


if __name__ == "__main__":
    conn = sqlite3.connect('ormuco_db.sqlite')

    listen_for_calls(conn)
