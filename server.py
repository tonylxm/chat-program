import socket
import threading
import hashlib
import ssl

# Define the server host and port
HOST = 'localhost'
PORT = 5555

class Server:
    def __init__(self, host, port):
        # SSL context for secure server connection
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile="cert.pem", keyfile="cert.key")
        self.context.set_ciphers('AES128-SHA')
        
        self.clients = {}
        self.passwords = {}
        self.lock = threading.Lock()
        
        # Bind and wrap the socket with SSL
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.socket = self.context.wrap_socket(self.socket, server_side=True)
        print('Secure server waiting for connections...')
        
        self.running = True
        self.accept_connections()

    def accept_connections(self):
        # Accept new connections in a loop
        while self.running:
            client_socket, client_address = self.socket.accept()
            print(f'Connection established with {client_address}')
            
            threading.Thread(target=self.client_handler, args=(client_socket, client_address)).start()

    def client_handler(self, client_socket, client_address):
        # Handle each client after authentication
        username = self.authenticate(client_socket)
        if username:
            with self.lock:
                self.clients[username] = client_socket
            self.receive_msg(client_socket, username)
        else:
            client_socket.close()

    def authenticate(self, client_socket):
        # Authenticate user by allowing registration or login
        try:
            while True:
                client_socket.send(b'Welcome! Register or login (R/L)')
                response = client_socket.recv(1024).decode('utf-8')
                if not response:
                    return None

                if response.upper() == 'R':
                    # Register new user
                    client_socket.send(b'Enter new username')
                    username = client_socket.recv(1024).decode('utf-8')
                    if not username:
                        return None
                    
                    client_socket.send(b'Enter new password')
                    password = client_socket.recv(1024).decode('utf-8')
                    if not password:
                        return None
                    
                    # Hash the password for secure storage
                    hashed_password = self.hash_password(password)

                    with self.lock:
                        if username not in self.passwords:
                            # Add new username and hashed password
                            self.passwords[username] = hashed_password
                            client_socket.send(b'Registration successful! You can now login.')
                            continue
                        else:
                            client_socket.send(b'Username already exists. Please try again.')
                            continue

                if response.upper() == 'L':
                    # Login existing user
                    client_socket.send(b'Enter your username')
                    username = client_socket.recv(1024).decode('utf-8')
                    if not username:
                        return None
                    
                    client_socket.send(b'Enter your password')
                    password = client_socket.recv(1024).decode('utf-8')
                    if not password:
                        return None
                    
                    # Hash the input password for comparison
                    hashed_password = self.hash_password(password)
                    
                    with self.lock:
                        # Check if username exists and password matches
                        if username not in self.passwords:
                            client_socket.send(b'Username not found. Please register first.')
                            continue
                        elif self.passwords[username] != hashed_password:
                            client_socket.send(b'Incorrect password. Please try again.')
                            continue
                        else:
                            client_socket.send(b'Login successful! Start chatting (type "exit" to quit).')
                            return username
                else:
                    client_socket.send(b'Invalid option. Please register or login (R/L)')
        except Exception as e:
            print(f"Error during authentication: {e}")
            return None

    def hash_password(self, password):
        # Hash password using SHA-256 for security
        return hashlib.sha256(password.encode()).hexdigest()

    def receive_msg(self, client_socket, username):
        # Receive and handle messages from the client
        try:
            while self.running:
                # Wait for a message from the client
                message = client_socket.recv(1024).decode('utf-8')
                
                if message.lower() == 'exit':
                    # Handle client disconnection
                    print(f"{username} has disconnected.")
                    with self.lock:
                        del self.clients[username]  # Remove client from dictionary
                    break
                
                # Broadcast the message to all other connected clients
                self.broadcast(f"{username}: {message}", client_socket)
                print(f"{username}: {message}")  # Display message on server console
        except ConnectionAbortedError:
            print("Connection aborted unexpectedly.")
        finally:
            client_socket.close()  # Close client socket when finished

    def broadcast(self, message, sender_socket):
        # Send message to all clients except the sender
        with self.lock:
            for client_socket in self.clients.values():
                if client_socket != sender_socket:
                    client_socket.send(message.encode('utf-8'))

if __name__ == "__main__":
    # Initialize the server
    Server(HOST, PORT)
