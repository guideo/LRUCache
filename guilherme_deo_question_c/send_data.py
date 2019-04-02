import socket
import pickle


if __name__ == "__main__":
    while True:
        try:
            key = input('Message to send: ')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('192.168.15.10', 8730))
            sock.sendall(pickle.dumps({'key': key}))
            print("Sent data: {}".format(key))
            data = sock.recv(1024)
            if data:
                data = pickle.loads(data)
            print("Result: {}".format(data))
            sock.close()
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
