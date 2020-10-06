import socket
import threading


class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.clientAddress = clientAddress

    def run(self):
        print("Connection from : ", clientAddress)
        self.csocket.send(bytes("Server connected\n", 'UTF-8'))
        msg = ''
        while True:
            try:
                data = self.csocket.recv(2048)
                # Take out newline from message
                msg = data.decode().rstrip()
                # If message empty then we close connection
                if not msg:
                    break
                print(f"[{clientAddress}]", msg)

                self.csocket.send(bytes("Message received\n", 'UTF-8'))
            except socket.timeout:
                break

        # Close connection

        self.csocket.send(bytes("Server disconnected\n", 'UTF-8'))
        print("Client at ", clientAddress, " disconnected...")

        # Close file descriptor
        self.csocket.close()
        threads.remove(self)

    def forceStop(self):
        # Close connection. This is used to interrupt recv.
        # SHUT_RD is used to stop reading but allow writing to file descriptor
        self.csocket.shutdown(socket.SHUT_RD)


LISTENING = "0.0.0.0"
PORT = 65432
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LISTENING, PORT))

print(f"Server started on {LISTENING}:{PORT}")

threads = []

try:
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        # Set timeout for 20 seconds
        clientsock.settimeout(20)
        newthread = ClientThread(clientAddress, clientsock)
        threads.append(newthread)
        newthread.start()
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    for t in threads:
        t.forceStop()
    server.close()
