import socket
import tqdm
import os

"""
Creating a communication server_socket:
Sources: 1) https://www.thepythoncode.com/article/send-receive-files-using-sockets-python
         2) https://www.geeksforgeeks.org/socket-programming-python/
"""

class Server(object):
    def __init__(self):
        self.s = None
        self.client_socket = None
        self.SERVER_HOST = "127.0.0.1"  # "192.168.56.1"  # device'server_socket IP address
        self.SERVER_PORT = 9990  # 80
        self.BUFFER_SIZE = 4096  # receive 4096 bits each time
        self.SEPARATOR = "<SEPARATOR>"
        self.TTI = 0
        self.ACK = "ACK"
        self.START_SIG = "START_SIG"
        self.START_SIG_ACK = "START_SIG_ACK"
        self.COMPLETION = "COMPLETION"
        self.file_received = False
        self.ack_sent = False

    def create_socket(self):
        # create the server server_socket
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[API Server][+] Socket successfully created")
        except socket.error as err:
            print("[API Server][-] Socket creation failed with error %s" % (err))
        # bind the server_socket to our local address
        self.s.bind((self.SERVER_HOST, self.SERVER_PORT))
        # enabling our server to accept connections; 5 here is the number of unaccepted connections that the system
        # will allow before refusing new connections
        self.s.listen(5)
        print(f"[API Server][*] Listening as {self.SERVER_HOST}:{self.SERVER_PORT}")

        # accept connection if there is any
        self.client_socket, address = self.s.accept()
        # if below code is executed, that means the sender is connected
        print(f"[API Server][+] {address} is connected.")
        self.handshake()

    def handshake(self):
        dataFromClient = self.client_socket.recv(1024)
        received_dataClient = dataFromClient.decode()
        print("[API Server][+] Three way-handshake: Receiving %s" % (received_dataClient))
        if received_dataClient == self.START_SIG:
            print("[API Server][+] Three way-handshake: Sending " + self.START_SIG_ACK)
            self.client_socket.send(self.START_SIG_ACK.encode())
            dataFromClient = self.client_socket.recv(1024)
            received_dataClient = dataFromClient.decode()
            print("[API Server][+] Three way-handshake: Receiving %s" % (received_dataClient))
        else:
            return

    def receive_time_message(self):
        dataFromClient = self.client_socket.recv(1024)
        received_dataClient = dataFromClient.decode()
        print("[API Server][+] Time report: Receiving %s" % (received_dataClient))

    def receive_files(self, sim):
        while True:
            next_reading_time = sim.mec_csv_distribution.next()
            yield sim.env.timeout(next_reading_time)
            # receive the file infos
            # receive using client server_socket, not server server_socket
            # mec_simulation.receive_time_message()
            received = None
            while received is None:
                received = self.client_socket.recv(self.BUFFER_SIZE).decode()
                # print("RECEIVED : ")
                # print(received)
            print("RECEIVED")
            print(received)
            # mec_simulation.client_socket.send(mec_simulation.ACK.encode()) # Function moved to external side
            # while mec_simulation.ack_sent is False:
            #     continue
            filename, filesize = received.split(self.SEPARATOR)
            # remove absolute path if there is
            filename = os.path.basename(filename)
            # convert to integer
            filesize = int(filesize)

            # start receiving the file from the server_socket
            # and writing to the file stream
            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "wb") as f:
                print("STARTED RECEIVING")
                while True:
                    # read 1024 bits from the server_socket (receive)
                    self.file_received = False
                    bytes_read = self.client_socket.recv(self.BUFFER_SIZE)
                    print("READING FROM CLIENT")
                    if not bytes_read:
                        self.file_received = True
                        print("FILE IS RECEIVED")
                        # nothing is received; file transmitting is done
                        break
                    elif bytes_read.decode() == self.COMPLETION:
                        bytes_read = None
                        f.close()
                        break
                    # write to the file the bits we just received
                    f.write(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))

    def send_ack(self):
        self.client_socket.send(self.ACK.encode())

    def close_socket(self):
        # close the client server_socket
        self.client_socket.close()
        # close the server server_socket
        self.s.close()
        print("[API Server][+] Socket closed successfully")


if __name__ == '__main__':
    server = Server()
    server.create_socket()
    server.receive_files()
    # server.close_socket()
