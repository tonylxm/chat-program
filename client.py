import socket
import threading
import sys

HOST = 'localhost'
PORT = 5555

class Client:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.username = None
        self.running = True
        self.is_authenticated = False
        
        while not self.is_authenticated:
            self.authenticate()
        self.talk()

    def authenticate(self):
        while True:
            response = self.client_socket.recv(1024).decode('utf-8')
            print(response)

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
                self.is_authenticated = True
                self.username = username
                break

    def talk(self):
        client_thread = threading.Thread(target=self.receive_msg)
        client_thread.start()
        self.send_msg()

    def send_msg(self):
        while self.running:
            message = input(f"{self.username}: ")

            if not message:
                print("Empty input, please try again.")
                continue
            if message.lower() == 'exit':
                self.client_socket.send(b'exit')
                self.running = False
                self.client_socket.close()
                sys.exit(0)

            self.client_socket.send(f"{self.username}: {message}".encode('utf-8'))

    def receive_msg(self):
        while self.running:
            try:
                server_message = self.client_socket.recv(1024).decode('utf-8')
                if server_message.lower() == 'exit':
                    print("\nServer has closed the connection.")
                    self.running = False
                    self.client_socket.close()
                    break

                print(f"\r{server_message}\n{self.username}: ", end="")
                sys.stdout.flush()
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                self.running = False
                break

if __name__ == "__main__":
    Client(HOST, PORT)
