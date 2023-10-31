# Author: Alba Jano
# Last Modified: 23.02.2022

import socket
import tqdm
import os


"""
Creating a communication socket:
Sources: 1) https://www.thepythoncode.com/article/send-receive-files-using-sockets-python
         2) https://www.geeksforgeeks.org/socket-programming-python/
"""

FILE_COUNTER = 0

class Server(object):
    def __init__(self):
        self.s = None
        self.client_socket = None
        self.SERVER_HOST = "0.0.0.0"  # device'socket IP address
        self.SERVER_PORT = 80
        self.BUFFER_SIZE = 4096  # receive 4096 num_of_bytes each time
        self.SEPARATOR = "<SEPARATOR>"

    def create_socket(self):
        # create the server socket
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[+]Socket successfully created")
        except socket.error as err:
            print("[-] Socket creation failed with error %s" % (err))

        # bind the socket to our local address
        self.s.bind((self.SERVER_HOST, self.SERVER_PORT))

        # enabling our server to accept connections
        # 5 here is the number of unaccepted connections that
        # the system will allow before refusing new connections
        self.s.listen(5)
        print(f"[*] Listening as {self.SERVER_HOST}:{self.SERVER_PORT}")

        # accept connection if there is any
        self.client_socket, address = self.s.accept()
        # if below code is executed, that means the sender is connected
        print(f"[+] {address} is connected.")

    def receive_files(self):
        # receive the file infos
        # receive using client socket, not server socket
        while True:
            received = self.client_socket.recv(self.BUFFER_SIZE).decode()
            filename, filesize = received.split(self.SEPARATOR)
            # remove absolute path if there is
            filename = os.path.basename(filename)
            # convert to integer
            filesize = int(filesize)

            # start receiving the file from the socket
            # and writing to the file stream

            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "wb") as f:
                while True:
                    # read 1024 num_of_bytes from the socket (receive)
                    bytes_read = self.client_socket.recv(self.BUFFER_SIZE)
                    if not bytes_read:
                        # nothing is received_msg
                        # file transmitting is done
                        break
                    # write to the file the num_of_bytes we just received_msg
                    f.write(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))

            # ack_message = 'ACK-' + str(FILE_COUNTER_LOCAL)
            # ack_message_bytes = num_of_bytes(ack_message)
            # mec_simulation.server_socket.send(ack_message.encode())

    def close_socket(self):
        # close the client socket
        self.client_socket.close()
        # close the server socket
        self.s.close()
        print("[+]Socket closed successfully")


if __name__ == '__main__':
    server = Server()
    server.create_socket()
    server.receive_files()
    server.close_socket()
