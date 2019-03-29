import socket


if __name__ == "__main__":
    while True:
        try:
            data = input('Message to send: ')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('192.168.15.10', 8730))
            sock.sendall(data.encode())
            print("Sent data: {}".format(data))
            data = sock.recv(1024)
            print("Result: {}".format(data.decode()))
            sock.close()
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED - Server is busy. \nERROR: {}".format(e))
