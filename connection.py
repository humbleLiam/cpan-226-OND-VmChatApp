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
        print(f"[DEBUG] send() called with message: '{message}'")
        print(f"[DEBUG] Mode: {self.mode}, Connected: {self.connected}")
        
        if self.mode == 'server' and not self.connection:
            print(f"[DEBUG] Server mode, trying to accept connection...")
            try:
                self.connection, address = self.sock.accept()
                self.connection.setblocking(False)
                self.connected = True
                print(f"Client connected from {address}")
            except BlockingIOError:
                print(f"[DEBUG] No incoming connection yet")
                return
        
        if self.mode == 'client' and not self.connected:
            print(f"[DEBUG] Client mode, checking connection status...")
            try:
                err = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err == 0:
                    self.connected = True
                    print(f"[DEBUG] Client connection established!")
                else:
                    print(f"[DEBUG] Client connection error: {err}")
            except Exception as e:
                print(f"[DEBUG] Error checking connection: {e}")
                return
    
        if not self.connected:
            print(f"[DEBUG] NOT CONNECTED - cannot send message")
            return
        
        print(f"[DEBUG] Connected! Attempting to send...")
        try:
            target = self.connection if self.mode == 'server' else self.sock
            print(f"[DEBUG] Sending to target socket: {target}")
            target.sendall(message.encode())
            print(f"[DEBUG] ✓ Message sent successfully!")
        except Exception as e:
            print(f"[DEBUG] ✗ Send error: {e}")

    def receive(self):
        # If server mode and no connection yet, try to accept
        if self.mode == 'server' and not self.connection:
            try:
                self.connection, addr = self.sock.accept()
                self.connection.setblocking(False)
                self.connected = True
                print(f"Client connected from {addr}")
            except BlockingIOError:
                return None
        
        # If client mode and not connected yet, check connection status
        if self.mode == 'client' and not self.connected:
            try:
                err = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err == 0:
                    self.connected = True
                    print(f"[DEBUG] Client connection completed!")
            except:
                return None
        
        if not self.connected:
            return None
        
        try:
            target = self.connection if self.mode == 'server' else self.sock
            data = target.recv(1024)
            if data:
                decoded = data.decode()
                print(f"[DEBUG] ✓ Received message: '{decoded}'")
                return decoded
        except BlockingIOError:
            return None
        except Exception as e:
            print(f"[DEBUG] Receive error: {e}")
        return None
    
    def startServer(self):
        print(f"Starting server on port {self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(1)
        self.sock.setblocking(False)
        print(f"Server listening on 0.0.0.0:{self.port}")
    
    def setUpClient(self):
        print(f"Connecting to {self.peer_ip}:{self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)

        try:
            self.sock.connect((self.peer_ip, self.port))
            self.connected = True
            print(f"Connected immediately to {self.peer_ip}:{self.port}")
        except BlockingIOError:
            print(f"Connecting to server... (non-blocking)")
        except Exception as e:
            print(f"Connection error - {e}")

    def findSocket(self):
        """Look for TCP connection on network by attempting to connect."""
        print(f"Searching for peer at {self.peer_ip}:{self.port}...")
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.settimeout(2)
        
        try:
            # Try to connect to peer
            test_sock.connect((self.peer_ip, self.port))
            test_sock.close()
            print(f"Found peer server at {self.peer_ip}:{self.port}")
            return True
        except:
            test_sock.close()
            print(f"No peer found, becoming server")
            return False
    
    def is_connected(self):
        """Check if connection is established."""
        return self.connected
    
    def close(self):
        """Close the connection."""
        try:
            if self.connection:
                self.connection.close()
            if self.sock:
                self.sock.close()
        except:
            pass