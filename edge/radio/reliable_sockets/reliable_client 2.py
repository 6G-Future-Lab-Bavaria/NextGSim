import socket
import os
import tqdm
import time

FILE_COUNTER_LOCAL = 0
ACK = "ACK"
ACK_MESSAGE = ACK.encode()
START_SIG = "START_SIG"
START_SIG_MESSAGE = START_SIG.encode()
START_SIG_ACK = "START_SIG_ACK"
START_SIG_ACK_MESSAGE = START_SIG_ACK.encode()
COMPLETION = "COMPLETION"
COMPLETION_MESSAGE = COMPLETION.encode()


class Client(object):
    def __init__(self, host, port, filename):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[+]Socket successfully created")
        except socket.error as err:
            print("[-] Socket creation failed with error %s" % err)

        self.server_IP = host  # the ip address or hostname of the server, the receiver
        self.server_port = port  # the port, let'socket use 5001
        self.filename = filename  # the name of file we want to send, make sure it exists
        self.SEPARATOR = "<SEPARATOR>"
        self.BUFFER_SIZE = 4096  # send 4096 bytes each time step
        self.filesize = os.path.getsize(self.filename)  # get the file size


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 9990  # 5001
    filename = "../edge/examples/RAN_MEC_v2.csv"
    client = Client(host, port, filename)
    counter = 0

    while True:
        try:
            client.socket.connect((client.server_IP, client.server_port))
            break
        except ConnectionRefusedError:
            client.socket.connect((client.server_IP, client.server_port))

    msg_rcv_sig = client.socket.recv(1024)
    msg_rcv_sig = msg_rcv_sig.decode()
    print("Client received_msg : ", msg_rcv_sig)

    client.socket.send(START_SIG_ACK_MESSAGE)

    time.sleep(1)

    while counter < 10:
        client.socket.send(
            f"{client.filename}{client.SEPARATOR}{client.filesize}{client.SEPARATOR}{FILE_COUNTER_LOCAL}".encode())
        progress = tqdm.tqdm(range(client.filesize), f"Sending {client.filename}", unit="B", unit_scale=True,
                             unit_divisor=1024)


        print("Sending file")



        with open(client.filename, "rb") as f:
            while True:
                print("Reading Bytes")
                # read the bytes from the file
                bytes_read = f.read(client.BUFFER_SIZE)
                print("Bytes Read")
                print(bytes_read)
                if not bytes_read:
                    print("Finished Sending")
                    client.socket.send(COMPLETION_MESSAGE)
                    # file transmitting is done
                    break
                # we use sendall to assure transmission in
                # busy networks
                # print("SENDING BYTES")
                # print(bytes_read)
                client.socket.send(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
                print("Waiting Message")
                received_message = client.socket.recv(client.BUFFER_SIZE).decode()
                print("received output_message")
                print(received_message)

                if received_message == ACK:
                    pass
                else:
                    raise SyntaxError

        print("CLIENT IS DONE SENDING")
        msg_received = client.socket.recv(1024)
        msg_received = msg_received.decode()
        if msg_received.startswith("Received File: "):
            print("msg_received")
            print(msg_received)
            FILE_COUNTER_LOCAL += 1
        else:
            raise Exception("Something is Wrong!")

        counter += 1
