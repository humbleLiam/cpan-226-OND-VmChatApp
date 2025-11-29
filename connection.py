import socket

class Connection():
    def __init__(self, peer_ip, port=5000):
        # Socket initialization tcp/  
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
        print(f"[SEND] Called with message: '{message}'")
        print(f"[SEND] Mode: {self.mode}, Connected: {self.connected}")
        
        if not self.confirmConnection():
            print(f"[SEND] confirmConnection() returned False - cannot send")
            return
    
        print(f"[SEND] Connection confirmed! Attempting to send...")
        try:
            target = self.connection if self.mode == 'server' else self.sock
            print(f"[SEND] Target socket: {target}")
            target.sendall(message.encode())
            print(f"[SEND] ✓ Message sent successfully!")
        except Exception as e:
            print(f"[SEND] ✗ Send error: {e}")

    def receive(self):
        if not self.confirmConnection():
            return None
        
        try:
            target = self.connection if self.mode == 'server' else self.sock
            data = target.recv(1024)
            if data:
                decoded = data.decode()
                print(f"[RECEIVE] ✓ Received message: '{decoded}'")
                return decoded
        except BlockingIOError:
            return None
        except Exception as e:
            print(f"[RECEIVE] Error: {e}")
        return None
    
    def startServer(self):
        print(f"[SERVER] Starting on port {self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(1)
        self.sock.setblocking(False)
        print(f"[SERVER] Listening on 0.0.0.0:{self.port}")
    
    def setUpClient(self):
        print(f"[CLIENT] Connecting to {self.peer_ip}:{self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        
        try:
            self.sock.connect((self.peer_ip, self.port))
            self.connected = True
            print(f"[CLIENT] Connected immediately!")
        except BlockingIOError:
            print(f"[CLIENT] Connection in progress (non-blocking mode)")
        except Exception as e:
            print(f"[CLIENT] Connection error: {e}")

    def findSocket(self):
        print(f"[FIND] Searching for peer at {self.peer_ip}:{self.port}...")
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.settimeout(2)
        
        try:
            # Try to connect to peer
            test_sock.connect((self.peer_ip, self.port))
            test_sock.close()
            print(f"[FIND] ✓ Found peer server at {self.peer_ip}:{self.port}")
            return True  # Peer is listening, we'll be client
        except:
            test_sock.close()
            print(f"[FIND] ✗ No peer found, becoming server")
            return False  # No peer listening
        
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

    def confirmConnection(self):
        print(f"[CONFIRM] Checking connection... Mode: {self.mode}, Connected: {self.connected}")
        
        if self.connected:
            print(f"[CONFIRM] Already connected!")
            return True
        
        if self.mode == 'server' and not self.connection:
            print(f"[CONFIRM] Server mode - trying to accept connection...")
            # Try to accept incoming connection
            try:
                self.connection, addr = self.sock.accept()
                self.connection.setblocking(False)
                self.connected = True
                print(f"[CONFIRM] ✓ Client connected from {addr}")
                return True
            except BlockingIOError:
                print(f"[CONFIRM] No incoming connection yet")
                return False
        
        if self.mode == 'client':
            print(f"[CONFIRM] Client mode - checking if connection completed...")
            # Check if non-blocking connection completed
            try:
                err = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                print(f"[CONFIRM] Socket error code: {err}")
                if err == 0:
                    self.connected = True
                    print(f"[CONFIRM] ✓ Client connection established!")
                    return True
                else:
                    print(f"[CONFIRM] Connection not ready yet (error: {err})")
                    return False
            except Exception as e:
                print(f"[CONFIRM] Exception checking connection: {e}")
                return False
        
        print(f"[CONFIRM] Returning False")
        return False