import socket
import importlib
import sqlite3
import re
from threading import Thread

cache_module = importlib.import_module('LRU_cache')
Cache = getattr(cache_module, 'Cache')


class CacheMaster:

    def __init__(self, size, db_conn):
        self.cache_list = {}
        self.cache_size = size
        self.lru_cache = Cache(self.cache_size, master=True, db_connection=db_conn)

    def listen_for_calls(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 8741))

        server_socket.listen(5)
        while True:
            print("Running Master...")

            client_socket, address = server_socket.accept()
            data = client_socket.recv(1024)
            data = data.decode()
            match = re.match(r'(.*?):(.*)', data)
            node_origin = match.group(1)
            data = match.group(2)
            return_data = ''
            print("Received request: {}".format(data))

            if 'NewCacheStarting' in data:
                match = re.match(r'NewCacheStarting (.*?):(.*)', data)
                new_address = match.group(1)
                new_port = int(match.group(2))
                self.register_node(node_origin, new_address, new_port)
                init_data = str(self.lru_cache)
                client_socket.sendall(init_data.encode())
            elif 'HitUpdate' in data:
                match = re.match(r'HitUpdate:(.*)', data)
                data = match.group(1)
                return_data = self.lru_cache.check_cache(data)
            else:
                return_data = self.lru_cache.check_cache(data)
                client_socket.sendall(return_data.encode())
            if return_data != "Object not found!" and 'NewCacheStarting' not in data:
                self.update_distributed_caches(data, node_origin)

            client_socket.close()

    def update_distributed_caches(self, update, origin):
        print("updating distributed caches")
        for cache_id, cache_info in self.cache_list.items():
            if cache_id != origin:
                print('update cache {}'.format(cache_id))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((cache_info['address'], cache_info['port'] + 1))
                sock.sendall(update.encode())
                sock.close()

    def register_node(self, node_id, address, port):
        self.cache_list[node_id] = {'address': address, 'port': port}


if __name__ == "__main__":
    conn = sqlite3.connect('ormuco_db.sqlite')

    cache_master = CacheMaster(3, conn)

    cache_master.listen_for_calls()
