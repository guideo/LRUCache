import socket


if __name__ == "__main__":
    while True:
        data = input('Message to send: ')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8730))
        print("Sent data: {}".format(sock.send(data.encode())))
        sock.close()
