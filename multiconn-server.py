import selectors
import socket
import types

sel = selectors.DefaultSelector()

host = "127.0.0.1"
port = 65432

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print("Accepted connection from ", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key,mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print("Closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
    
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("Echoing", repr(data.outb), "to", data.addr)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("Listening on" , (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    # Block until there are sockets ready for I/O
    events = sel.select(timeout=None)
    for key, mask in events:
        # When key.data is none, connection needs to be accepted
        if key.data is None:
            # Pass socket object
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)