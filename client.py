import socket
import threading
import sys

HOST = 'localhost'
PORT = 5555

class Client:
    def __init__(self, HOST, PORT):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        self.username = "Client"
        self.running = True
        self.talk()

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

                sys.stdout.write('\r' + ' ' * 50 + '\r')
                sys.stdout.write(f"{server_message}\n")
                sys.stdout.write("Client: ")
                sys.stdout.flush()
            except ConnectionResetError:
                print("\nConnection lost. The server may have closed the connection.")
                self.running = False
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                self.running = False
                break

if __name__ == "__main__":
    Client(HOST, PORT)
