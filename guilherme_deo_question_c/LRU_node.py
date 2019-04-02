import socket
import importlib
import argparse
import sys
import pickle
from threading import Thread

cache_module = importlib.import_module('LRU_cache')
Cache = getattr(cache_module, 'Cache')


def parse_input(args):
    parser = argparse.ArgumentParser(description='Receives an address and port and start a Cache Node')
    parser.add_argument('address', type=str, help='String for the address')
    parser.add_argument('port', type=int, help='Integer for the port')

    parsed = parser.parse_args(args)
    return parsed


class CacheNode:

    def __init__(self, address, port):
        self.port = port
        self.address = address
        self.lru_cache = Cache()

    def listen_for_calls(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.address, self.port))

        server_socket.listen(5)
        while True:
            print("Running...")
            client_socket, address = server_socket.accept()
            data = client_socket.recv(self.lru_cache.data_size)
            data = pickle.loads(data)
            if data['key'] == "print":
                print(self.lru_cache.cache_dll)
            else:
                print("Data: {}".format(data['key']))
                return_data = self.lru_cache.check_cache(data['key'])
                print('return data: {}'.format(return_data))
                client_socket.sendall(pickle.dumps({'data': return_data}))
            client_socket.close()

    def listen_for_updates(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.address, self.port + 1))

        server_socket.listen(5)
        while True:
            print("Waiting for updates...")
            client_socket, address = server_socket.accept()
            data = client_socket.recv(self.lru_cache.data_size)
            data = pickle.loads(data)
            print("Data: {}".format(data))
            if data['id'] == self.lru_cache.cache_id:
                self.lru_cache.check_cache(data['key'], data['data'])
            else:
                print('invalid cache id')
            client_socket.close()

    def init_cache(self):
        try:
            db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            db_socket.connect((self.lru_cache.master_address, self.lru_cache.master_port))
            db_socket.sendall(pickle.dumps({'id': self.lru_cache.cache_id,
                                            'request_type': 'NewCacheStarting',
                                            'address': self.address,
                                            'port': self.port}))
            data = db_socket.recv(self.lru_cache.data_size * self.lru_cache.max_size)
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
        finally:
            db_socket.close()
        if data is not None:
            data = pickle.loads(data)
        self.lru_cache.build(data['data'])
        print(data)


if __name__ == "__main__":
    info = parse_input(sys.argv[1:])
    cache_node = CacheNode(info.address, info.port)

    cache_node.init_cache()

    thread = Thread(target=cache_node.listen_for_updates)
    thread.start()

    cache_node.listen_for_calls()
