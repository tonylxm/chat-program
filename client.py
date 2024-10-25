import socket
import threading
import sys
import ssl

# Define the server host and port
HOST = 'localhost'
PORT = 5555

class Client:
    def __init__(self, host, port):
        # SSL context for secure client connection
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        
        # Load the server's self-signed certificate
        self.context.load_verify_locations('cert.pem')
        
        # Disable hostname verification for self-signed certificates
        self.context.check_hostname = False
        
        # Create a socket and wrap it with SSL
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = self.context.wrap_socket(self.client_socket, server_hostname=host)
        
        try:
            # Connect to the server
            self.client_socket.connect((host, port))
            print("Connected to the server.")
        except ssl.SSLError as ssl_err:
            print(f"SSL error: {ssl_err}")
            sys.exit(1)
        except Exception as e:
            print(f"Error connecting to server: {e}")
            sys.exit(1)
        
        self.username = None
        self.running = True
        self.is_authenticated = False
        
        # Authenticate the client with the server
        while not self.is_authenticated:
            self.authenticate()
        
        # Start chatting
        self.talk()

    def authenticate(self):
        while True:
            try:
                # Receive server message and display it
                response = self.client_socket.recv(1024).decode('utf-8')
                if not response:
                    print("Disconnected from the server.")
                    self.running = False
                    break
                print(response)

                # Based on the server's prompt, take the appropriate input from the user
                if 'Register or login' in response:
                    option = input("Enter R to register or L to login: ")
                    self.client_socket.send(option.encode('utf-8'))
                elif 'Enter new username' in response or 'Enter your username' in response:
                    username = input(">> ")
                    self.client_socket.send(username.encode('utf-8'))
                elif 'Enter new password' in response or 'Enter your password' in response:
                    password = input(">> ")
                    self.client_socket.send(password.encode('utf-8'))
                elif 'Login successful' in response:
                    # If login is successful, set the authenticated flag and store the username
                    self.is_authenticated = True
                    self.username = username
                    print(f"Welcome, {self.username}!")
                    break

            except Exception as e:
                print(f"An error occurred during authentication: {e}")
                self.running = False
                break

    def talk(self):
        # Start a thread to handle receiving messages from the server
        client_thread = threading.Thread(target=self.receive_msg)
        client_thread.start()
        
        # Start sending messages to the server
        self.send_msg()

    def send_msg(self):
        # Handle sending messages to the server
        while self.running:
            message = input(f"{self.username}: ")

            # Check for empty input
            if not message:
                print("Empty input, please try again.")
                continue
            # If user types 'exit', close the connection
            if message.lower() == 'exit':
                self.client_socket.send(b'exit')
                self.running = False
                self.client_socket.close()
                print("Disconnected from the server.")
                sys.exit(0)

            # Send the message to the server
            self.client_socket.send(message.encode('utf-8'))

    def receive_msg(self):
        # Handle receiving and displaying messages from the server
        while self.running:
            try:
                # Wait for a message from the server
                server_message = self.client_socket.recv(1024).decode('utf-8')
                if not server_message:
                    self.running = False
                    break

                # If the server closes the connection, handle it
                if server_message.lower() == 'exit':
                    print("\nServer has closed the connection.")
                    self.running = False
                    self.client_socket.close()
                    break

                # Display the received message and prompt user for the next input
                print(f"\r{server_message}\n{self.username}: ", end="")
                sys.stdout.flush()
            except Exception as e:
                print(f"\nAn error occurred while receiving messages: {e}")
                self.running = False
                break

if __name__ == "__main__":
    # Initialize the client
    Client(HOST, PORT)
