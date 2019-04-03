import socket
import importlib
import pickle

cache_module = importlib.import_module('LRU_cache')
Cache = getattr(cache_module, 'Cache')


class CacheMaster:

    def __init__(self):
        self.cache_list = {}
        self.cache_lookup = {}
        self.lru_cache = Cache(master=True)

    def listen_for_calls(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.lru_cache.master_address, self.lru_cache.master_port))

        server_socket.listen(5)
        while True:
            print("Running Master...")

            client_socket, address = server_socket.accept()
            data = client_socket.recv(self.lru_cache.data_size)
            data = pickle.loads(data)
            node_id = data['id']
            return_data = ''
            print("Received request: {}".format(data))

            if 'request_type' in data and data['request_type'] == 'NewCacheStarting':
                new_address = data['address']
                new_port = data['port']
                self.register_node(node_id, new_address, new_port)
                init_data = str(self.lru_cache)
                client_socket.sendall(pickle.dumps({'data': init_data}))
            elif 'request_type' in data and data['request_type'] == 'HitUpdate':
                return_data = self.lru_cache.check_cache(data['key'])
            else:
                return_data = self.lru_cache.check_cache(data['key'])
                client_socket.sendall(pickle.dumps({'data': return_data}))
            if return_data != "Object not found!" and ('request_type' not in data or data['request_type'] != 'NewCacheStarting'):
                self.update_distributed_caches(data['key'], return_data, node_id)

            client_socket.close()

    def update_distributed_caches(self, key, data, origin):
        if not self.lru_cache.replicate:
            return
        print("updating distributed caches")
        update = {'key': key, 'data': data}
        updated_cache_list = dict(self.cache_list)
        for cache_id, cache_info in self.cache_list.items():
            update['id'] = cache_id
            if cache_id != origin:
                try:
                    print('update cache {}'.format(cache_id))
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((cache_info['address'], cache_info['port'] + 1))
                    sock.sendall(pickle.dumps(update))
                except ConnectionRefusedError as e:
                    print("CONNECTION REFUSED - Could not contact node {}. \nERROR: {}".format(cache_id, e))
                    print("Removing node from cache_list")
                    updated_cache_list.pop(cache_id)
                finally:
                    sock.close()
        self.cache_list = dict(updated_cache_list)

    def register_node(self, node_id, address, port):
        self.cache_list[node_id] = {'address': address, 'port': port}
        # Inversion (key value) for invalidating old cache which had same ip:port
        inv = '{}:{}'.format(address, port)
        if inv in self.cache_lookup:
            self.cache_list.pop(self.cache_lookup[inv])
            print('Invalidating old cache ({}) on same IP:PORT'.format(self.cache_lookup[inv]))
        self.cache_lookup[inv] = node_id


if __name__ == "__main__":
    cache_master = CacheMaster()

    cache_master.listen_for_calls()
