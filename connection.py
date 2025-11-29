import socket
import time

class Connection():
    def __init__(self, peer_ip, port=5000):
        # Socket initialization tcp/  
        self.sock = None
        self.connection = None
        self.mode = None
        self.peer_ip = peer_ip
        self.port = port
        self.connected = False
        self.setup_attempted = False

        # Determine role based on IP (lower IP = server)
        my_ip = self.get_my_ip()
        if my_ip < peer_ip:
            self.mode = 'server'
            self.startServer()
        else:
            self.mode = 'client'
            self.setUpClient()
    
    def get_my_ip(self):
        """Get local IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "192.168.100.255"  # Fallback to high IP

    def send(self, message):
        print(f"\n[SEND] >>> Sending message: '{message}'")
        
        if not self.confirmConnection():
            print(f"[SEND] ✗ Not connected, cannot send")
            return
    
        try:
            target = self.connection if self.mode == 'server' else self.sock
            target.sendall(message.encode())
            print(f"[SEND] ✓ Message sent successfully!\n")
        except Exception as e:
            print(f"[SEND] ✗ Send error: {e}\n")

    def receive(self):
        if not self.confirmConnection():
            return None
        
        try:
            target = self.connection if self.mode == 'server' else self.sock
            data = target.recv(1024)
            if data:
                decoded = data.decode()
                print(f"\n[RECEIVE] <<< Got message: '{decoded}'\n")
                return decoded
        except BlockingIOError:
            return None
        except Exception as e:
            # Only print error if we're supposedly connected
            if self.connected:
                print(f"[RECEIVE] Error: {e}")
                self.connected = False
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
            print(f"[CLIENT] Connection initiated...")
        except BlockingIOError:
            print(f"[CLIENT] Connection in progress...")
        except Exception as e:
            print(f"[CLIENT] Connection error: {e}")
    
    def is_connected(self):
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