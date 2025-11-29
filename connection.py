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
        print(f"\n[SEND] >>> Sending message: '{message}'")
        
        if not self.confirmConnection():
            print(f"[SEND] ✗ Not connected, cannot send")
            return
    
        try:
            target = self.connection if self.mode == 'server' else self.sock
            print(f"[DEBUG SEND] Mode: {self.mode}, using socket: {target}")
            target.sendall(message.encode())
            print(f"[SEND] ✓ Message sent successfully!\n")
        except Exception as e:
            print(f"[SEND] ✗ Send error: {e}\n")
            print(f"[DEBUG] Mode: {self.mode}, self.connection: {self.connection}, self.sock: {self.sock}")

    def receive(self):
        if not self.confirmConnection():
            return None
        
        try:
            target = self.connection if self.mode == 'server' else self.sock
            print(f"[DEBUG RECEIVE] Mode: {self.mode}, using socket: {target}")
            data = target.recv(1024)
            if data:
                decoded = data.decode()
                print(f"\n[RECEIVE] <<< Got message: '{decoded}'\n")
                return decoded
        except BlockingIOError:
            return None
        except Exception as e:
            print(f"[RECEIVE] Error: {e}")
            print(f"[DEBUG] Mode: {self.mode}, self.connection: {self.connection}, self.sock: {self.sock}")
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
            # Don't set self.connected = True here!
            # Let confirmConnection() verify the connection is ready
            print(f"[CLIENT] Connection initiated...")
        except BlockingIOError:
            print(f"[CLIENT] Connection in progress...")
        except Exception as e:
            print(f"[CLIENT] Connection error: {e}")

    def findSocket(self):
        print(f"[FIND] Searching for peer at {self.peer_ip}:{self.port}...")
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.settimeout(2)
        
        try:
            test_sock.connect((self.peer_ip, self.port))
            test_sock.close()
            print(f"[FIND] Found peer server!")
            return True
        except:
            test_sock.close()
            print(f"[FIND] No peer found, becoming server")
            return False
        
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
        # QUIET MODE - only print when connection state changes
        
        if self.connected:
            return True
        
        if self.mode == 'server' and not self.connection:
            try:
                self.connection, addr = self.sock.accept()
                self.connection.setblocking(False)
                self.connected = True
                print(f"\n[CONNECTION] ✓ Client connected from {addr}\n")
                return True
            except BlockingIOError:
                # Silently return False - no connection yet
                return False
            except Exception as e:
                print(f"[DEBUG] Server accept error: {e}")
                return False
        
        if self.mode == 'client':
            try:
                # Just check the socket error status
                err = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err == 0:
                    if not self.connected:
                        self.connected = True
                        print(f"\n[CONNECTION] ✓ Client connection established!\n")
                    return True
                return False
            except Exception as e:
                return False
        
        return False
    