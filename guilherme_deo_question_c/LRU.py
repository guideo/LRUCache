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
        additional_data = client_socket.recv(1024)
        count = 1
        while additional_data:
            count += 1
            additional_data = client_socket.recv(1024)
            data += additional_data
        print("{}: {}".format(count, data))
        print(check_cache(data, cache_dll, cache_dict))
        client_socket.close()


def check_cache(key, cache_dll, cache_dict):
    if key in cache_dict:
        element = cache_dict[key]['element']
        cache_dict[key]['timestamp'] = time.time()
        cache_dll.hit(element)
        return "Hit"
    else:
        new_node = DLLNode(data=key)
        last_ele = cache_dll.fault(new_node)
        if last_ele:
            cache_dict.pop(last_ele)
        cache_dict[key] = {'element': new_node, 'timestamp': time.time()}
        return "Fault"


if __name__ == "__main__":
    lru_dll = CacheDLL()
    lru_dict = {}

    listen_for_calls(lru_dll, lru_dict)
