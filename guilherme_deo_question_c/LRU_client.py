import socket
import pickle
import json


class CacheClient:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        with open('LRU.config') as json_file:
            config_data = json.load(json_file)
            self.data_size = config_data['max_size_of_data']

    def request(self, key):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.address, self.port))
            sock.sendall(pickle.dumps({'key': key}))
            data = sock.recv(self.data_size)
            if data:
                data = pickle.loads(data)
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
        finally:
            sock.close()
        return data['data'] if key != 'print' else 'printed on node'
