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
        self.server_socket = None
        self.server_IP = host  # the ip address or hostname of the server, the receiver
        self.server_port = port  # the port, let'server_socket use 5001
        # self.filename = '/Users/mehmetmertbese/Desktop/NextGSim/results/RAN.csv'
        # fixme: relative directories are unstable
        self.filename = 'RAN_Client.csv'
        # the name of file we want to send, make sure it exists
        self.SEPARATOR = "<SEPARATOR>"
        self.BUFFER_SIZE = 4096  # send 4096 bits each time step
        self.filesize = 0  # get the file size
        self.ACK = "ACK"
        self.START_SIG = "START_SIG"
        self.START_SIG_ACK = "START_SIG_ACK"
        self.FILE_READY_SIG = "FILE_READY"
        self.COMPLETION = "COMPLETION"
        self.dataFromServer = None

    def create_socket(self):
        # create the client server_socket
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[API Client][+] Socket successfully created")
        except socket.error as err:
            print("[API Client][-] Socket creation failed with error %s" % (err))

        print(f"[API Client][+] Connecting to {self.server_IP}:{self.server_port}")
        self.server_socket.connect((self.server_IP, self.server_port))
        print("[API Client][+] Connected.")
        self.handshake()

    def handshake(self):
        self.server_socket.settimeout(10)
        print("[API Client][+] Three way-handshake: Sending " + self.START_SIG)
        self.server_socket.send(self.START_SIG.encode())
        try:
            self.dataFromServer = self.server_socket.recv(1024)
        except socket.error as err:
            print("[API Client][-] Socket creation failed with error %s" % (err))
        received_dataServer = self.dataFromServer.decode()
        print("[API Client][+] Three way-handshake: Receiving %s" % (received_dataServer))
        if received_dataServer == self.START_SIG_ACK:
            self.server_socket.send(self.START_SIG_ACK.encode())
            print("[API Client][+] Three way-handshake: Sending " + self.START_SIG_ACK)
        else:
            return

    def send_time_message(self, message: str):
        self.server_socket.send(message.encode())
        print("[API Client][+] Time report: Sending " + message)

    def send_and_receive_file(self):
        # send the filename and filesize
        # client.send_time_message(message="TTI 1")
        self.dataFromServer = None
        self.server_socket.send(self.START_SIG.encode())
        # self.server_socket.send(f"{self.filename}{self.SEPARATOR}{self.filesize}".encode())
        # file_to_be_sent = os.pardir + '/' + self.filename  # fixme: this is a workaround to be fixed
        # self.filesize = os.path.getsize(file_to_be_sent)
        try:
            # time.sleep(0.01)
            self.dataFromServer = self.server_socket.recv(1024)
        except socket.error as err:
            print("[API Client][-] Data reception failed with %s" % (err))
        received_dataServer = self.dataFromServer.decode()
        if received_dataServer == self.ACK:
            # # start sending the file
            # progress = tqdm.tqdm(range(self.filesize), f"Sending {self.filename}", unit="B", unit_scale=True,
            #                      unit_divisor=1024)
            # bytes_read = None
            # with open(file_to_be_sent, "rb") as f:
            #     while True:
            #         # read the bits from the file
            #         bytes_read = f.read(self.BUFFER_SIZE)
            #         if not bytes_read:
            #             # file transmitting is done
            #             self.server_socket.send(self.COMPLETION.encode())
            #             break
            #         # we use sendall to assure transmission in busy networks
            #         self.server_socket.sendall(bytes_read)
            #         time.sleep(0.05)
            #         # update the progress bar
            #         progress.update(len(bytes_read))
            # progress.close()
            # print("[API Client][+] Sent file ")
            self.server_socket.send(self.FILE_READY_SIG.encode())
            # time.sleep(0.01)

        ###############################
        # File Processing Code
        ###############################

        try:
            self.dataFromServer = self.server_socket.recv(1024)
        except socket.error as err:
            print("[API Client][-] Socket creation failed with error %s" % (err))

        received_dataServer = self.dataFromServer.decode()
        if received_dataServer == "FILE_RECEIVED":
            print("\n[API Server][+] Received file ")

        # received = self.server_socket.recv(self.BUFFER_SIZE).decode()
        # self.server_socket.send(self.ACK.encode())
        # filename, filesize = received.split(self.SEPARATOR)
        # # remove absolute path if there is
        # filename = os.path.basename(filename)
        # # convert to integer
        # filesize = int(filesize)
        #
        # recv_file = os.pardir + '/MEC_Client.csv'
        #
        # # start receiving the file from the server_socket
        # # and writing to the file stream
        # progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        # with open(recv_file, "wb") as f:
        #     while True:
        #         # read 1024 bits from the server_socket (receive)
        #         bytes_read = self.server_socket.recv(self.BUFFER_SIZE)
        #         if not bytes_read:
        #             # nothing is received; file transmitting is done
        #             continue
        #         elif bytes_read.decode() == self.COMPLETION:
        #             bytes_read = None
        #             f.close()
        #             break
        #         # write to the file the bits we just received
        #         f.write(bytes_read)
        #         # update the progress bar
        #         progress.update(len(bytes_read))
        # progress.close()

        print("\n[API Server][+] Received file ")

    def close_socket(self):
        # close the server_socket
        self.server_socket.close()
        print("[API Client][+] Socket closed successfully")


# if __name__ == '__main__':
#     host = "127.0.0.1"  # "192.168.1.101"
#     port = 9990  # 5001
#     # filename = "data.csv"
#     filename = "./RAN.csv"
#     client = Client(host, port, filename)
#     client.create_socket()
#     time.sleep(0.5)
#     for _ in range(0, 20):
#         client.send_and_receive_file()
#         time.sleep(1)
#     client.close_socket()
