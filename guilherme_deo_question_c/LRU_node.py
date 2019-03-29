import socket
import importlib

cache_module = importlib.import_module('LRU_cache')
Cache = getattr(cache_module, 'Cache')


def listen_for_calls(lru_cache):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('192.168.15.10', 8730))

    server_socket.listen(5)
    while True:
        print("Running...")
        client_socket, address = server_socket.accept()
        print(client_socket)
        print(address)
        data = client_socket.recv(1024)
        data = data.decode()
        print("Data: {}".format(data))
        return_data = lru_cache.check_cache(data)
        client_socket.sendall(return_data.encode())
        client_socket.close()


def init_cache():
    try:
        db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_socket.connect(('localhost', 8741))
        db_socket.sendall('NewCacheStarting'.encode())
        data = db_socket.recv(1024)
        info = ''
        while data:
            info += data
            data = db_socket.recv(1024)
        db_socket.close()
    except ConnectionRefusedError as e:
        print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
    if data is not None:
        data = data.decode()
    # process data
    print(data)


if __name__ == "__main__":
    cache = Cache()

    init_cache()

    listen_for_calls(cache)
