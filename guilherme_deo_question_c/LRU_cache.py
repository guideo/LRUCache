import importlib
import time
import socket
import re
import uuid
from threading import Lock

cache_dll_module = importlib.import_module('CacheDoubleLinkedList')
CacheDLL = getattr(cache_dll_module, 'CacheDoubleLinkedList')
DLLNode = getattr(cache_dll_module, 'Node')


class Cache:

    def __init__(self, size, master=False, db_connection=None):
        self.cache_id = uuid.uuid4().hex
        self.master = master
        self.db_connection = db_connection
        self.lock = Lock()
        self.max_size = size
        self.cache_dll = CacheDLL(self.max_size)
        self.cache_dict = {}

    def check_cache(self, key):
        if key in self.cache_dict:
            if not self.master:
                self.update_master_hit(key)
            with self.lock:
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
                with self.lock:
                    new_node = DLLNode(key=key, data=data)
                    last_ele = self.cache_dll.fault(new_node)
                    if last_ele is not None:
                        self.cache_dict.pop(last_ele)
                    self.cache_dict[key] = {'element': new_node, 'timestamp': time.time()}
                    return new_node.data
            else:
                return "Object not found!"

    def update_master_hit(self, key):
        try:
            db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            db_socket.connect(('localhost', 8741))
            db_socket.sendall('{}:HitUpdate:{}'.format(self.cache_id, key).encode())
            db_socket.close()
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))

    def request_data_from_db(self, key):
        data = None
        try:
            db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            db_socket.connect(('localhost', 8741))
            db_socket.sendall('{}:{}'.format(self.cache_id, key).encode())
            data = db_socket.recv(1024)
            db_socket.close()
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
        if data is not None:
            data = data.decode()
        return data

    def get_data_from_db(self, key):
        c = self.db_connection.cursor()
        c.execute('SELECT * FROM users WHERE name="{}"'.format(key))
        return str(c.fetchall())

    def __str__(self):
        node = self.cache_dll.tail
        output = ''
        while node:
            output += '(<{}>, <{}>)'.format(node.key, node.data)
            node = node.prev_node
        return output

    def build(self, string_representation):
        ele_list = re.findall(r'(\(<.*?>\))', string_representation)
        for ele in ele_list:
            match = re.match(r'\(<(.*?)>, <(.*?)>\)', ele)
            key = match.group(1)
            data = match.group(2)
            new_node = DLLNode(key=key, data=data)
            self.cache_dll.fault(new_node)
            self.cache_dict[key] = {'element': new_node, 'timestamp': time.time()}
