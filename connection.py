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


        if not self.findSocket():
            self.startServer()
            self.mode = 'server'
        else:
            self.setUpClient()
            self.mode = 'client'


    def send(self, message):

        if self.mode =='server' and not self.connection:
            try:
                self.connection, address = self.sock.accept()
                self.connection.setblocking(False)
                self.connected = True
            except BlockingIOError:
                return
        if self.mode == 'client' and not self.connected:
            try:
                err = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err == 0:
                    self.connected = True
            except:
                return  # Still connecting
    
        if not self.connected:
            return
    
        try:
            target = self.connection if self.mode == 'server' else self.sock
            target.sendall(message.encode())
        except Exception as e:
            print("Send error:", e)


    def receive(self):
        # If server mode and no connection yet, try to accept
        if self.mode == 'server' and not self.connection:
            try:
                self.connection, addr = self.sock.accept()
                self.connection.setblocking(False)
                self.connected = True
                print(f"Client connected from {addr}")
            except BlockingIOError:
                return None  # No connection yet
        
        # If client mode and not connected yet, check connection status
        if self.mode == 'client' and not self.connected:
            try:
                err = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err == 0:
                    self.connected = True
            except:
                return None  # Still connecting
        
        if not self.connected:
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
            self.connected = True 
        except BlockingIOError:
            print(f"connecting to server")
        except Exception as e:
            print(f"error -{e}")

    def findSocket (self):
        # to do write a function that looks for tcp connection on netwok with ack request. 
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.settimeout(2)  
        
        try:
            #try to connect to peer
            test_sock.connect((self.peer_ip, self.port))
            test_sock.close()
            print(f"Found peer server at {self.peer_ip}:{self.port}")
            return True  # Peer is listening we'll be client
        except:
            test_sock.close()
            return False # no peer listening
        
    def is_connected(self):
        return self.connected

    def close(self):
        try:
            if self.connection:
                self.connection.close()
            if self.sock:
                self.sock.close()
        except:
            pass