# Author: Alba Jano
# Last Modified: 23.02.2022

import socket
import tqdm
import os
import time

"""
Creating a communication server_socket:
Sources: 1) https://www.thepythoncode.com/article/send-receive-files-using-sockets-python
         2) https://www.geeksforgeeks.org/socket-programming-python/
"""


class Client(object):
    def __init__(self, host, port, filename):
        self.s = None
        self.server_IP = host  # the ip address or hostname of the server, the receiver
        self.server_port = port  # the port, let'server_socket use 5001
        self.filename = filename  # the name of file we want to send, make sure it exists
        self.SEPARATOR = "<SEPARATOR>"
        self.BUFFER_SIZE = 4096  # send 4096 bits each time step
        self.filesize = os.path.getsize(self.filename)  # get the file size
        self.ACK = "ACK"
        self.START_SIG = "START_SIG"
        self.START_SIG_ACK = "START_SIG_ACK"
        self.COMPLETION = "COMPLETION"
        self.dataFromServer = None

    def create_socket(self):
        # create the client server_socket
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[API Client][+] Socket successfully created")
        except socket.error as err:
            print("[API Client][-] Socket creation failed with error %s" % (err))

        print(f"[API Client][+] Connecting to {self.server_IP}:{self.server_port}")
        self.s.connect((self.server_IP, self.server_port))
        print("[API Client][+] Connected.")
        self.handshake()

    def handshake(self):
        self.s.settimeout(10)
        print("[API Client][+] Three way-handshake: Sending " + self.START_SIG)
        self.s.send(self.START_SIG.encode())
        try:
            self.dataFromServer = self.s.recv(1024)
        except socket.error as err:
            print("[API Client][-] Socket creation failed with error %s" % (err))
        received_dataServer = self.dataFromServer.decode()
        print("[API Client][+] Three way-handshake: Receiving %s" % (received_dataServer))
        if received_dataServer == self.START_SIG_ACK:
            self.s.send(self.START_SIG_ACK.encode())
            print("[API Client][+] Three way-handshake: Sending " + self.START_SIG_ACK)
        else:
            return

    def send_time_message(self, message: str):
        self.s.send(message.encode())
        print("[API Client][+] Time report: Sending " + message)

    def send_file(self):
        # send the filename and filesize
        # client.send_time_message(output_message="TTI 1")
        self.dataFromServer = None
        self.s.send(f"{self.filename}{self.SEPARATOR}{self.filesize}".encode())
        print("SENDING DATA")
        try:
            time.sleep(0.5)
            self.dataFromServer = self.s.recv(1024)
            print("DATA FROM SERVER")
            print(self.dataFromServer)
        except socket.error as err:
            print("[API Client][-] Data reception failed with %s" % (err))
        received_dataServer = self.dataFromServer.decode()
        print("RECEIVED DATA FROM SERVER")
        print(received_dataServer)
        if received_dataServer == self.ACK:
            print("SENDING FILE")
            # start sending the file
            progress = tqdm.tqdm(range(self.filesize), f"Sending {self.filename}", unit="B", unit_scale=True,
                                 unit_divisor=1024)
            bytes_read = None
            with open(self.filename, "rb") as f:
                while True:
                    # read the bits from the file
                    bytes_read = f.read(self.BUFFER_SIZE)
                    progress.update(len(bytes_read))
                    if not bytes_read:
                        # file transmitting is done
                        self.s.send(self.COMPLETION.encode())
                        break
                    # we use sendall to assure transmission in busy networks
                    self.s.sendall(bytes_read)
                    # update the progress bar

                progress.close()
            print("[API Client][+] Sent file ")

    def receive_file(self):
        # receive the file infos
        # receive using client server_socket, not server server_socket
        # mec_simulation.receive_time_message()
        received = None
        while received is None or received == '':
            received = self.s.recv(self.BUFFER_SIZE).decode()
        self.s.send(self.ACK.encode())
        filename, filesize = received.split(self.SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)

        # start receiving the file from the server_socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True,
                             unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # read 1024 bits from the server_socket (receive)
                self.file_received = False
                bytes_read = self.s.recv(self.BUFFER_SIZE)
                if not bytes_read:
                    self.file_received = True
                    # nothing is received; file transmitting is done
                    break
                elif bytes_read.decode() == self.COMPLETION:
                    bytes_read = None
                    f.close()
                    break
                progress.update(len(bytes_read))
                # write to the file the bits we just received
                f.write(bytes_read)
                # update the progress bar



    def close_socket(self):
        # close the server_socket
        self.s.close()
        print("[API Client][+] Socket closed successfully")


if __name__ == '__main__':
    # host = "131.159.205.180"  # "192.168.1.101"
    host = "127.0.0.1"  # "192.168.1.101"
    port = 9990  # 5001
    # filename = "data.csv"
    filename = "RAN_MEC.csv"
    client = Client(host, port, filename)
    client.create_socket()
    for i in range(0, 20):
        client.send_file()
        client.receive_file()
        time.sleep(1)
    client.close_socket()
