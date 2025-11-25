import socket

class Connection():
    def __init__(self,peer_ip, port=5000):


        #socket intialization tcp/  
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False) 
        self.peer_ip = peer_ip
        self.port = port

        try:
            self.sock.connect((peer_ip, port)) # expects tuple
        except BlockingIOError:
            pass
        except ConnectionRefusedError:
            print('Peer not running.')



    def send(self, message):
        try:
            self.sock.sendall(message.encode())
        except Exception as e:
            print("Send error:", e)

    def receive(self):
        try:
            data = self.sock.recv(1024)
            if data:
                return data.decode()
        except BlockingIOError:
            return None
        except Exception as e:
            print("Receive error:", e)
        return None
