import socket

class Connection():
    def __init__(self,peer_ip, port=5000):
        #socket intialization tcp/  
        self.sock = None
        self.connection = None
        self.mode = None
        self.peer_ip = peer_ip
        self.port = port
        self.connected = False

        my_ip = self.getIp()
        if my_ip <peer_ip:
            self.mode ='server'
            self.startServer()
        else:
            self.mode = 'client'
            self.setUpClient()


    def send(self, message):

        if not self.confirmConnection():
            return
    
        try:
            target = self.connection if self.mode == 'server' else self.sock
            target.sendall(message.encode())
        except Exception as e:
            print("Send error:", e)


    def receive(self):
        if not self.confirmConnection():
            return None
        
        try:
            target = self.connection if self.mode == 'server' else self.sock
            data = target.recv(1024)
            if data:
                return data.decode()
        except BlockingIOError:
            return None
        except Exception as e:
            print("Receive error:", e)
        return None
    
    def startServer(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(1)
        self.sock.setblocking(False)
    
    def setUpClient(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.sock.setblocking(False) 
        try:
            self.sock.connect((self.peer_ip, self.port))
        except BlockingIOError:
            print(f"connecting to server")
        except Exception as e:
            print(f"error -{e}")

    def close(self):
        try:
            if self.connection:
                self.connection.close()
            if self.sock:
                self.sock.close()
        except:
            pass


    def confirmConnection(self):
        if self.connected:
            return True
        
        if self.mode == 'server' and not self.connection:
            # Try to accept incoming connection
            try:
                self.connection, addr = self.sock.accept()
                self.connection.setblocking(False)
                self.connected = True
                print(f"Client connected from {addr}")
                return True
            except BlockingIOError:
                return False
        
        if self.mode == 'client':
            # Check if non-blocking connection completed
            try:
                err = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err == 0:
                    if not self.connected:
                        self.connected = True
                        print(f"Client connection established!")
                    return True
                return False
            except:
                return False
        
        return False
    def getIp(self):
        try:
           # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #s.connect(("8.8.8.8", 80))
           # ip = s.getsockname()[0]
           # s.close()
            hostname=socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except:
            return "192.168.100.255"