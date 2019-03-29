import importlib
import time
import socket

cache_dll_module = importlib.import_module('CacheDoubleLinkedList')
CacheDLL = getattr(cache_dll_module, 'CacheDoubleLinkedList')
DLLNode = getattr(cache_dll_module, 'Node')


class Cache:

    def __init__(self, master=False, db_connection=None):
        self.master = master
        self.db_connection = db_connection
        self.cache_dll = CacheDLL(3)
        self.cache_dict = {}

    def check_cache(self, key):
        if key in self.cache_dict:
            element = self.cache_dict[key]['element']
            self.cache_dict[key]['timestamp'] = time.time()
            self.cache_dll.hit(element)
            return element.data
        else:
            if self.master:
                data = self.get_data_from_db(key)
            else:
                data = self.request_data_from_db(key)
            if data is not None and data != '[]':
                new_node = DLLNode(key=key, data=data)
                last_ele = self.cache_dll.fault(new_node)
                if last_ele is not None:
                    self.cache_dict.pop(last_ele)
                self.cache_dict[key] = {'element': new_node, 'timestamp': time.time()}
                return new_node.data
            else:
                return "Object not found!"

    @staticmethod
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
        print(data)
        return data

    def get_data_from_db(self, key):
        c = self.db_connection.cursor()
        c.execute('SELECT * FROM users WHERE name="{}"'.format(key))
        return str(c.fetchall())
