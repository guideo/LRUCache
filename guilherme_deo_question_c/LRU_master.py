import socket
import importlib
import sqlite3
from threading import Thread

cache_module = importlib.import_module('LRU_cache')
Cache = getattr(cache_module, 'Cache')


def listen_for_calls(lru_cache, connection):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8741))

    server_socket.listen(5)
    while True:
        print("Running Master...")

        client_socket, address = server_socket.accept()
        print(server_socket)
        print(client_socket)
        data = client_socket.recv(1024)
        data = data.decode()
        print("Received request: {}".format(data))

        if data == 'NewCacheStarting':
            init_data = ''
            client_socket.sendall(init_data.encode())
            pass
        elif 'HitUpdate' in data:
            pass
        else:
            data = lru_cache.get_data_from_db(data)
            client_socket.sendall(data.encode())

        client_socket.close()


def update_distributed_caches(cache_list, update):
    for c in cache_list:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((c['address'], c['port']))
        sock.sendall(update.encode())
        sock.close()


if __name__ == "__main__":
    conn = sqlite3.connect('ormuco_db.sqlite')

    cache = Cache(master=True, db_connection=conn)

    listen_for_calls(cache, conn)
