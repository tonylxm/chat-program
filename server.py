import socket
import threading
import hashlib

HOST = 'localhost'
PORT = 5555

class Server:
    def __init__(self, host, port):
        self.clients = {}
        self.passwords = {}
        self.lock = threading.Lock()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        print('Server waiting for connections...')
        
        self.running = True
        self.accept_connections()

    def accept_connections(self):
        while self.running:
            client_socket, client_address = self.socket.accept()
            print(f'Connection established with {client_address}')
            
            threading.Thread(target=self.client_handler, args=(client_socket, client_address)).start()

    def client_handler(self, client_socket, client_address):
        username = self.authenticate(client_socket)
        if username:
            with self.lock:
                self.clients[username] = client_socket
            self.receive_msg(client_socket, username)
        else:
            client_socket.close()

    def authenticate(self, client_socket):
        try:
            while True:
                client_socket.send(b'Welcome! Register or login (R/L)')
                response = client_socket.recv(1024).decode('utf-8')
                if not response:
                    return None

                if response.upper() == 'R':
                    client_socket.send(b'Enter new username')
                    username = client_socket.recv(1024).decode('utf-8')
                    if not username:
                        return None
                    
                    client_socket.send(b'Enter new password')
                    password = client_socket.recv(1024).decode('utf-8')
                    if not password:
                        return None
                    
                    hashed_password = self.hash_password(password)

                    with self.lock:
                        if username not in self.passwords:
                            self.passwords[username] = hashed_password
                            client_socket.send(b'Registration successful! You can now login.')
                            continue
                        else:
                            client_socket.send(b'Username already exists. Please try again.')
                            continue

                if response.upper() == 'L':
                    client_socket.send(b'Enter your username')
                    username = client_socket.recv(1024).decode('utf-8')
                    if not username:
                        return None
                    
                    client_socket.send(b'Enter your password')
                    password = client_socket.recv(1024).decode('utf-8')
                    if not password:
                        return None
                    
                    hashed_password = self.hash_password(password)
                    
                    with self.lock:
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
        return hashlib.sha256(password.encode()).hexdigest()

    def receive_msg(self, client_socket, username):
        try:
            while self.running:
                message = client_socket.recv(1024).decode('utf-8')
                
                if message.lower() == 'exit':
                    print(f"{username} has disconnected.")
                    with self.lock:
                        del self.clients[username]
                    break
                
                # Broadcast the message to all other clients
                self.broadcast(f"{username}: {message}", client_socket)
                print(f"{username}: {message}")
        except ConnectionAbortedError:
            print("Connection aborted unexpectedly.")
        finally:
            client_socket.close()

    def broadcast(self, message, sender_socket):
        with self.lock:
            for client_socket in self.clients.values():
                if client_socket != sender_socket:
                    client_socket.send(message.encode('utf-8'))

if __name__ == "__main__":
    Server(HOST, PORT)
