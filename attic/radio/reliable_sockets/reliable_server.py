# import socket
# import os
# import time
# from datetime import datetime
#
# import tqdm
#
# FILE_COUNTER_LOCAL = 0
# ACK = "ACK"
# ACK_MESSAGE = ACK.encode()
# START_SIG = "START_SIG"
# START_SIG_MESSAGE = START_SIG.encode()
# START_SIG_ACK = "START_SIG_ACK"
# START_SIG_ACK_MESSAGE = START_SIG_ACK.encode()
# COMPLETION = "COMPLETION"
# COMPLETION_MESSAGE = COMPLETION.encode()
# RAN_DATA_READ_FLAG = False
#
#
# class Server:
#     def __init__(mec_simulation):
#         mec_simulation.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         mec_simulation.SERVER_HOST = "131.159.192.148"
#         mec_simulation.SERVER_PORT = 9990
#         mec_simulation.BUFFER_SIZE = 4096
#         mec_simulation.SEPARATOR = "<SEPARATOR>"
#
#     def start_server(mec_simulation, mec_simulation):
#         global FILE_COUNTER_LOCAL
#         mec_simulation.socket.bind((mec_simulation.SERVER_HOST, mec_simulation.SERVER_PORT))
#         mec_simulation.socket.listen(5)
#         client_socket, addr = mec_simulation.socket.accept()
#         client_socket.send(START_SIG_MESSAGE)
#
#         print("Sent start signal")
#         received_msg = client_socket.recv(mec_simulation.BUFFER_SIZE).decode()
#         print("Server received_msg : ", received_msg)
#         new_filename = 'RAN_MEC_server_' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '.csv'
#         if received_msg == START_SIG_ACK:
#             pass
#         else:
#             print("Wrong Message")
#
#         received_msg = client_socket.recv(mec_simulation.BUFFER_SIZE).decode()
#
#         if received_msg == START_SIG:
#             while True:
#                 try:
#                     received_msg = client_socket.recv(mec_simulation.BUFFER_SIZE).decode()
#                     filename, filesize, file_counter = received_msg.split(mec_simulation.SEPARATOR)
#                     print("filename")
#                     print(filename)
#                     print("filesize")
#                     print(filesize)
#                     print("file counter")
#                     print(file_counter + "\n")
#                     # remove absolute path if there is
#                     # filename = os.path.basename(filename)
#                     # convert to integer
#                     filesize = int(filesize)
#
#                     # start receiving the file from the socket
#                     # and writing to the file stream
#
#                     progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True,
#                                          unit_divisor=1024)
#                     # with open(filename, "wb") as f:
#
#                     with open(new_filename, "wb") as f:
#                         while True:
#                             # read 1024 bits from the socket (receive)
#                             # print("Waiting bits")
#                             bytes_read = client_socket.recv(mec_simulation.BUFFER_SIZE)
#                             if bytes_read.decode() == COMPLETION:
#                                 print("File Transfer Completed")
#                                 # nothing is received_msg
#                                 # file transmitting is done
#                                 break
#                             # write to the file the bits we just received_msg
#                             # print("BYTES READ")
#                             # print(bytes_read)
#                             f.write(bytes_read)
#                             # update the progress bar
#                             progress.update(len(bytes_read))
#                             client_socket.send(ACK_MESSAGE)
#
#                     SendReceptionACK(client_socket, file_counter)
#                     FILE_COUNTER_LOCAL += 1
#                     print("IM HERE")
#
#                     yield mec_simulation.env.timeout(mec_simulation.ran_csv_read_distribution.next())
#
#
#                 except KeyboardInterrupt:
#                     client_socket.close()
# #
# #
# def SendReceptionACK(server_socket, file_counter):
#     reception_ack = "Received File: " + str(file_counter)
#     print(reception_ack)
#     server_socket.send(reception_ack.encode())
#
#
#
#
# if __name__ == '__main__':
#     server = Server()
#     server.socket.bind((server.SERVER_HOST, server.SERVER_PORT))
#     server.socket.listen(100)
#     client_socket, addr = server.socket.accept()
#     client_socket.send(START_SIG_MESSAGE)
#     # server.socket.bind((server.SERVER_HOST, server.SERVER_PORT))
#     # server.socket.listen(5)
#     # server_socket, addr = server.socket.accept()
#     # server_socket.send(START_SIG_MESSAGE)
#
#     print("Sent start signal")
#     received_msg = client_socket.recv(server.BUFFER_SIZE).decode()
#     if received_msg == START_SIG_ACK:
#         pass
#     else:
#         print("Wrong Message")
#
#     print("Server received_msg : ", received_msg)
#     new_filename = 'RAN_MEC_server_' + datetime.today().strftime('%Y-%m-%d') + '.csv'
#
#     received_msg = client_socket.recv(server.BUFFER_SIZE).decode()
#     print("Server received_msg : ", received_msg)
#
#     if received_msg != START_SIG:
#         print("Wrong output_message")
#     else:
#         pass
#
#     received_msg = client_socket.recv(server.BUFFER_SIZE).decode()
#     print("tti")
#     print(received_msg)
#     received_msg = client_socket.recv(server.BUFFER_SIZE).decode()
#     filename, filesize = received_msg.split(server.SEPARATOR)
#     print("filename")
#     print(filename)
#     print("filesize")
#     print(filesize)
#
#     # remove absolute path if there is
#     # filename = os.path.basename(filename)
#     # convert to integer
#     filesize = int(filesize)
#
#     # start receiving the file from the socket
#     # and writing to the file stream
#
#     progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True,
#                          unit_divisor=1024)
#     # with open(filename, "wb") as f:
#
#     with open(new_filename, "wb") as f:
#         while True:
#             # read 1024 bits from the socket (receive)
#             # print("Waiting bits")
#             bytes_read = client_socket.recv(server.BUFFER_SIZE)
#             # if bytes_read.decode() == COMPLETION:
#             #     print("File Transfer Completed")
#             #     # nothing is received_msg
#             #     # file transmitting is done
#             #     break
#             if not bytes_read:
#                 break
#             # write to the file the bits we just received_msg
#             # print("BYTES READ")
#             # print(bytes_read)
#             f.write(bytes_read)
#             # update the progress bar
#             progress.update(len(bytes_read))
#
#     client_socket.send(ACK_MESSAGE)
#     SendReceptionACK(client_socket, FILE_COUNTER_LOCAL)
#     FILE_COUNTER_LOCAL += 1
#     print("IM HERE")

# Author: Alba Jano
# Last Modified: 23.02.2022

import socket
import tqdm
import os
import pandas as pd

"""
Creating a communication socket:
Sources: 1) https://www.thepythoncode.com/article/send-receive-files-using-sockets-python
         2) https://www.geeksforgeeks.org/socket-programming-python/
"""

class Server(object):
    def __init__(self):
        self.s = None
        self.client_socket = None
        self.SERVER_HOST = "131.159.192.148"  # device's IP address
        self.SERVER_PORT = 9990
        self.BUFFER_SIZE = 4096  # receive 4096 bits each time
        self.SEPARATOR = "<SEPARATOR>"
        self.TTI = 0
        self.ACK = "ACK"
        self.START_SIG = "START_SIG"
        self.START_SIG_ACK = "START_SIG_ACK"
        self.COMPLETION = "COMPLETION"

    def create_socket(self):
        # create the server socket
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[+]Socket successfully created")
            # mec_simulation.handshake()
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

        # mec_simulation.handshake()



    def handshake(self):
        # mec_simulation.s.send(mec_simulation.START_SIG.encode())
        dataFromClient = self.s.recv(1024)
        print(dataFromClient.decode())
        if dataFromClient.decode() != self.START_SIG:
            return
        else:
            # dataFromClient = mec_simulation.s.recv(1024)
            # print(dataFromClient.decode())
            # if dataFromClient.decode() != mec_simulation.START_SIG:
                # return
            self.client_socket.send(self.START_SIG.encode())
            dataFromClient = self.s.recv(1024)
            if dataFromClient.decode() != self.START_SIG_ACK:
                return


    def receive_files(self):
        # receive the file infos
        # receive using client socket, not server socket

        # received_TTI = mec_simulation.client_socket.recv(mec_simulation.BUFFER_SIZE).decode('utf-8')
        # print("RAN simulator time"+str(received_TTI))
        received = self.client_socket.recv(self.BUFFER_SIZE).decode('utf-8')
        print('received')
        print(received)
        filename, filesize = received.split(self.SEPARATOR)
        print('filename')
        print(filename)
        print('filesize')
        print(filesize)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)

        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # read 1024 bits from the socket (receive)
                bytes_read = self.client_socket.recv(self.BUFFER_SIZE)
                print(bytes_read)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bits we just received
                f.write(bytes_read)
                f.truncate(0)
                # update the progress bar
                progress.update(len(bytes_read))

        # mec_simulation.s.send(mec_simulation.ACK.encode())

    def close_socket(self):
        # close the client socket
        self.client_socket.close()
        # close the server socket
        self.s.close()
        print("[+]Socket closed successfully")


if __name__ == '__main__':
    server = Server()
    server.create_socket()
    # server.handshake()
    while True:
        server.receive_files()
    # server.close_socket()


# import socket
# import hashlib
# import threading
# import struct
#
# HOST = '131.159.192.148'
# PORT = 9990
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))
# s.listen(10)
# print("Waiting for a connection.....")
#
# conn, addr = s.accept()
# print("Got a connection from ", addr)
#
# while True:
#     hash_type = conn.recv(1024)
#     print('hash service_type: ', hash_type)
#     if not hash_type:
#         break
#
#     file_name = conn.recv(1024)
#     print('file name: ', file_name)
#
#     file_size = conn.recv(1024)
#     file_size = int(file_size, 2)
#     print('file size: ', file_size)
#
#     f = open(file_name, 'wb')
#     chunk_size = 4096
#     while file_size > 0:
#         if file_size < chunk_size:
#             chuk_size = file_size
#         data = conn.recv(chunk_size)
#     f.write(data)
#     file_size -= len(data)
#
# f.close()
# print('File received successfully')
# s.close()

# import socket
# import pickle
#
# server_socket = socket.socket()
# server_socket.bind(('131.159.192.148', 9990))  # local server-client
#
# server_socket.listen(3)  # Max. 3 connections
# print('Waiting for connection')
#
# Buffer = []
# i = 0
#
# while True:
#     client_socket, addr = server_socket.accept()
#     received_data = client_socket.recv(1024).decode()
#     print('Client address', addr, received_data)
#
#     client_socket.recv(pickle.loads(Buffer)).decode()
#     print(Buffer[i])
#     i = + 1
#
#     if i == 10000:
#         client_socket.close()  # Closing server socket
#     else:
#         continue
