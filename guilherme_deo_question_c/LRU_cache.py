import importlib
import time
import socket
import uuid
import json
import pickle
import sqlite3
from random import randint
from threading import Lock, Thread

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
    master_list = {}
    master_lookup = {}

    def __init__(self, address, port, master=False):
        self.cache_id = uuid.uuid4().hex
        self.address = address
        self.port = port
        self.master = master
        self.lock = Lock()
        self.cache_dict = {}

        with open('LRU.config') as json_file:
            config_data = json.load(json_file)

            if self.master:
                self.db_connection = sqlite3.connect(config_data['db'])
            else:
                self.db_connection = None
            self.max_size = config_data['max_size_of_cache']
            self.cache_dll = CacheDLL(self.max_size)
            self.expiration_seconds = config_data['cache_expiration_time_seconds']
            self.data_size = config_data['max_size_of_data']
            self.hard_expire = config_data['hard_expire']
            self.replicate = config_data['replicate']

        self.init_cache()

        print(Cache.master_list)
        print(Cache.master_list == True)
        if not Cache.master_list and not self.master:
            print('There is no master registered yet.')
            print('Please start a Master Cache before trying to start a Node.')
            return
        elif not self.master:
            selected_master = randint(0, len(Cache.master_list))
            self.master_address = Cache.master_list[selected_master]['address']
            self.master_port = Cache.master_list[selected_master]['port']
        else:
            print('here')
            Cache.master_list[self.cache_id] = {'address': self.address, 'port': self.port}
            inv = '{}:{}'.format(self.address, self.port)
            if inv in Cache.master_lookup:
                Cache.master_list.pop(Cache.master_lookup[inv])
                print('Invalidating old MASTER ({}) on same IP:PORT'.format(Cache.master_lookup[inv]))
            Cache.master_lookup[inv] = self.cache_id
            print(Cache.master_list)

        thread = Thread(target=self.listen_for_updates)
        thread.start()

    def clear_outdated_data(self):
        node = self.cache_dll.tail
        if self.hard_expire:
            while node:
                aux_node = node.prev_node
                if (time.time() - self.expiration_seconds) > self.cache_dict[node.key]['timestamp']:
                    removed_ele = self.cache_dll.delete_ele(node)
                    print('Clearing outdated data: {}'.format(removed_ele))
                    self.cache_dict.pop(removed_ele)
                node = aux_node
        else:
            while node and (time.time() - self.expiration_seconds) > self.cache_dict[node.key]['timestamp']:
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
                if not self.hard_expire:
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

    def listen_for_updates(self):
        if not self.replicate:
            return
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.address, self.port + 1))

        server_socket.listen(5)
        while True:
            print("Waiting for updates...")
            client_socket, address = server_socket.accept()
            data = client_socket.recv(self.data_size)
            data = pickle.loads(data)
            print("Data: {}".format(data))
            if data['id'] == self.cache_id:
                self.check_cache(data['key'], data['data'])
            else:
                print('invalid cache id')
            client_socket.close()

    def init_cache(self):
        if not self.replicate:
            return
        if not Cache.master_list:
            print('No MASTER node found')
            return
        try:
            db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            db_socket.connect((self.master_address, self.master_port))
            db_socket.sendall(pickle.dumps({'id': self.cache_id,
                                            'request_type': 'NewCacheStarting',
                                            'address': self.address,
                                            'port': self.port}))
            data = db_socket.recv(self.data_size * self.max_size)
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
        finally:
            db_socket.close()
        if data is not None:
            data = pickle.loads(data)
        self.build(data['data'])
        print(data)

    def update_master_hit(self, key):
        if not self.replicate:
            return
        try:
            db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            db_socket.connect((self.master_address, self.master_port))
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
            db_socket.connect((self.master_address, self.master_port))
            db_socket.sendall(pickle.dumps({'id': self.cache_id, 'key': key}))
            data = db_socket.recv(self.data_size)
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
            output[node.key] = {'data': node.data, 'timestamp': self.cache_dict[node.key]['timestamp']}
            node = node.prev_node
        return json.dumps(output)

    def build(self, string_representation):
        ele_dict = json.loads(string_representation)
        print(ele_dict)
        for key, data in ele_dict.items():
            new_node = DLLNode(key=key, data=data['data'])
            self.cache_dll.fault(new_node)
            self.cache_dict[key] = {'element': new_node, 'timestamp': data['timestamp']}
