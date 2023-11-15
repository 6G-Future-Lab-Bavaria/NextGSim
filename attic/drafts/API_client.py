import socket
import time

import tqdm
import os

"""
Creating a communication socket:
Sources: 1) https://www.thepythoncode.com/article/send-receive-files-using-sockets-python
         2) https://www.geeksforgeeks.org/socket-programming-python/
"""

FILE_COUNTER = 1


class Client(object):
    def __init__(self, host, port, filename):
        self.socket = None
        self.server_IP = host  # the ip address or hostname of the server, the receiver
        self.server_port = port  # the port, let'socket use 5001
        self.filename = filename  # the name of file we want to send, make sure it exists
        self.SEPARATOR = "<SEPARATOR>"
        self.BUFFER_SIZE = 4096  # send 4096 num_of_bytes each time step
        self.filesize = os.path.getsize(self.filename)  # get the file size

    def create_socket(self):
        # create the client socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[+]Socket successfully created")
        except socket.error as err:
            print("[-] Socket creation failed with error %s" % (err))

        print(f"[+] Connecting to {self.server_IP}:{self.server_port}")
        self.socket.connect((self.server_IP, self.server_port))
        print("[+] Connected.")

    def send_file(self):
        # send the filename and filesize
        while True:
            self.socket.send(f"{self.filename}{self.SEPARATOR}{self.filesize}".encode())

            # start sending the file
            progress = tqdm.tqdm(range(self.filesize), f"Sending {self.filename}", unit="B", unit_scale=True,
                                 unit_divisor=1024)
            with open(self.filename, "rb") as f:
                while True:
                    # read the num_of_bytes from the file
                    bytes_read = f.read(self.BUFFER_SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transmission in
                    # busy networks
                    self.socket.sendall(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))

            # print('Server sent:', mec_simulation.socket.recv(1024).decode())
            # time.sleep(1)



    def close_socket(self):
        # close the socket
        self.socket.close()
        print("[+]Socket closed successfully")


if __name__ == '__main__':
    host = "127.0.0.1"  # "192.168.1.101"
    port = 80  # 5001
    filename = "../csv_files/RAN_MEC_v2.csv"
    client = Client(host, port, filename)
    client.create_socket()
    client.send_file()
    client.close_socket()
