import importlib
import time
import socket
import uuid
import json
import pickle
from threading import Lock

cache_dll_module = importlib.import_module('CacheDoubleLinkedList')
CacheDLL = getattr(cache_dll_module, 'CacheDoubleLinkedList')
DLLNode = getattr(cache_dll_module, 'Node')


class CacheMessage:

    def __init__(self, cache_id=None, request_type=None, key=None, data=None):
        self.cache_id = cache_id
        self.request_type = request_type
        self.key = key
        self.data = data

    def dumps(self):
        data = {'id': self.cache_id, 'request_type': self.request_type,
                'key': self.key, 'data': self.data}
        return pickle.dumps(data)

    def loads(self, message):
        data = pickle.loads(message)
        self.cache_id = data['cache_id']
        self.request_type = data['request_type']
        self.key = data['key']
        self.data = data['data']


class Cache:

    def __init__(self, size, master=False, db_connection=None):
        self.cache_id = uuid.uuid4().hex
        self.master = master
        self.db_connection = db_connection
        self.lock = Lock()
        self.max_size = size
        self.cache_dll = CacheDLL(self.max_size)
        self.cache_dict = {}

    def clear_outdated_data(self):
        node = self.cache_dll.tail
        while node and (time.time() - 30) > self.cache_dict[node.key]['timestamp']:
            print(self.cache_dict[node.key]['timestamp'])
            print(time.time() + 30)
            removed_ele = self.cache_dll.delete_last()
            print('Clearing outdated data: {}'.format(removed_ele))
            self.cache_dict.pop(removed_ele)
            node = self.cache_dll.tail

    def check_cache(self, key, update_data=None):
        with self.lock:
            self.clear_outdated_data()
            if key in self.cache_dict:
                if not self.master and update_data is None:
                    self.update_master_hit(key)

                element = self.cache_dict[key]['element']
                self.cache_dict[key]['timestamp'] = time.time()
                self.cache_dll.hit(element)
                return element.data
            else:
                if update_data is not None:
                    data = update_data
                elif self.master:
                    data = self.get_data_from_db(key)
                else:
                    data = self.request_data_from_db(key)
                if data is not None and data != 'Object not found!':
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
            db_socket.sendall(pickle.dumps({'id': self.cache_id,
                                            'request_type': 'HitUpdate',
                                            'key': key}))
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
        finally:
            db_socket.close()

    def request_data_from_db(self, key):
        data = None
        try:
            db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            db_socket.connect(('localhost', 8741))
            db_socket.sendall(pickle.dumps({'id': self.cache_id, 'key': key}))
            data = db_socket.recv(1024)
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
        finally:
            db_socket.close()
        if data is not None:
            data = pickle.loads(data)
        return data['data']

    def get_data_from_db(self, key):
        c = self.db_connection.cursor()
        c.execute('SELECT * FROM users WHERE name="{}"'.format(key))
        output = c.fetchall()
        return str(output) if len(output) > 0 else "Object not found!"

    def __str__(self):
        node = self.cache_dll.tail
        output = {}
        while node:
            output[node.key] = node.data
            node = node.prev_node
        return json.dumps(output)

    def build(self, string_representation):
        ele_dict = json.loads(string_representation)
        for key, data in ele_dict.items():
            new_node = DLLNode(key=key, data=data)
            self.cache_dll.fault(new_node)
            self.cache_dict[key] = {'element': new_node, 'timestamp': time.time()}
