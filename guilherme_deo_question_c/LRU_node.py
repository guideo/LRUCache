import socket
import time
import importlib

cache_dll_module = importlib.import_module('CacheDoubleLinkedList')
CacheDLL = getattr(cache_dll_module, 'CacheDoubleLinkedList')
DLLNode = getattr(cache_dll_module, 'Node')


def listen_for_calls(cache_dll, cache_dict):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8730))

    server_socket.listen(5)
    while True:
        print("Running...")
        client_socket, address = server_socket.accept()
        data = client_socket.recv(1024)
        data = data.decode()
        print("Data: {}".format(data))
        return_data = check_cache(data, cache_dll, cache_dict)
        client_socket.sendall(return_data.encode())
        client_socket.close()


def check_cache(key, cache_dll, cache_dict):
    print(cache_dll)
    print(cache_dict)
    if key in cache_dict:
        element = cache_dict[key]['element']
        cache_dict[key]['timestamp'] = time.time()
        cache_dll.hit(element)
        return element.data
    else:
        data = request_data_from_db(key)
        if data is not None:
            new_node = DLLNode(key=key, data=data)
            last_ele = cache_dll.fault(new_node)
            if last_ele is not None:
                cache_dict.pop(last_ele)
            cache_dict[key] = {'element': new_node, 'timestamp': time.time()}
            return new_node.data
        else:
            return "Object not found!"


def request_data_from_db(key):
    data = None
    try:
        db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_socket.connect(('localhost', 8741))
        db_socket.sendall(key.encode())
        data = db_socket.recv(1024)
        db_socket.close()
    except ConnectionRefusedError as e:
        print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
    if data is not None:
        data = data.decode()
    return data


if __name__ == "__main__":
    lru_dll = CacheDLL(3)
    lru_dict = {}

    listen_for_calls(lru_dll, lru_dict)
