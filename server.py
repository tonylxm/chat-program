import socket
import threading
import sys

HOST = 'localhost'
PORT = 5555

class Server:    
    def __init__(self, HOST, PORT):
        self.clients = {}
        self.lock = threading.Lock()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        print('Server waiting for connection...')
        client_socket, client_address = self.socket.accept()
        print(f'Connection established with {client_address}')
        self.running = True
        
        username = None
        while username is None:
            username = self.authenticate(client_socket)
        if username is None:
            print(f"Connection lost during authentication with {client_address}")
            client_socket.close()
        
        self.talk(client_socket)
        
    def authenticate(self, client_socket):
        try:
            while True:
                client_socket.send(b'Welcome! Register or login: (R/L)')
                response = client_socket.recv(1024).decode('utf-8')
                if not response:
                    return None

                if response.upper() == 'R':
                    client_socket.send(b'Enter new username')
                    username = client_socket.recv(1024).decode('utf-8')
                    if not username:
                        return None
                    with self.lock:
                        if username not in self.clients:
                            self.clients[username] = client_socket
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
                    with self.lock:
                        if username not in self.clients:
                            client_socket.send(b'Username not found. Please register first.')
                            continue
                        else:
                            client_socket.send(b'Login successful! Start chatting (type "exit" to quit).')
                            return username
                else:
                    client_socket.send(b'Invalid option. Please register or login (R/L)')

        except Exception as e:
            print(f"Error during authentication: {e}")
            return None
    
    def talk(self, client_socket):
        client_thread = threading.Thread(target=self.receive_msg, args=(client_socket,))
        client_thread.start()
        self.send_msg(client_socket)
        
        client_thread.join()

    def send_msg(self, client_socket):
        while self.running:
            message = input("Server: ")
            
            if not message:
                print("Empty input, please try again.")
                continue

            if message.lower() == 'exit':
                client_socket.send(b'exit')
                self.running = False
                client_socket.close()
                self.socket.close()
                sys.exit(0)
            
            client_socket.send(f"Server: {message}".encode('utf-8'))

    def receive_msg(self, client_socket):
        try:
            while self.running:
                client_message = client_socket.recv(1024).decode('utf-8')
                
                if client_message.lower() == 'exit':
                    print("\nConnection closed by the client.")
                    self.running = False
                    client_socket.close()
                    self.socket.close()
                    break
                
                sys.stdout.write('\r' + ' ' * 50 + '\r')
                sys.stdout.write(f"{client_message}\n")
                sys.stdout.write("Server: ")
                sys.stdout.flush()
        except ConnectionAbortedError:
            print("Connection aborted unexpectedly.")
        finally:
            client_socket.close()

if __name__ == "__main__":
    Server(HOST, PORT)
