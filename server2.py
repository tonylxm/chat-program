import socket
import threading

clients = {}  # Stores username-socket key-pairs locally
lock = threading.Lock()

HOST = 'localhost'
PORT = 5555

def authenticate(client_socket):
    try:
        while True:
            client_socket.send(b'Welcome! Register or login: (R/L)')
            response = client_socket.recv(1024).decode('utf-8')
            if not response:
                return None

            if response.upper() == 'R':
                client_socket.send(b'Enter new username:')
                username = client_socket.recv(1024).decode('utf-8')
                if not username:
                    return None
                with lock:
                    if username not in clients:
                        client_socket.send(b'Registration successful! You can now login.')
                        continue
                    else:
                        client_socket.send(b'Username already exists. Please try again.')
                        continue

            elif response.upper() == 'L':
                client_socket.send(b'Enter your username:')
                username = client_socket.recv(1024).decode('utf-8')
                if not username:
                    return None
                with lock:
                    if username not in clients:
                        client_socket.send(b'Username not found. Please register first.')
                        continue
                    else:
                        client_socket.send(b'Login successful! Start chatting (type "exit" to quit).')
                        return username
            else:
                client_socket.send(b'Invalid option. Please register or login (R/L)')
                continue
    except Exception as e:
        print(f"Error during authentication: {e}")
        return None

def handle_client(client_socket, client_address):
    username = None
    while username is None:
        username = authenticate(client_socket)

    if username is None:
        print(f"Connection lost during authentication with {client_address}")
        client_socket.close()
        return

    try:
        with lock:
            clients[username] = client_socket  # Add user to the clients dictionary after successful login

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message.lower() == 'exit':
                break
            print(f"{username}: {message}")
            with lock:
                for sock in clients.values():
                    if sock != client_socket:
                        sock.send(f"{username}: {message}".encode('utf-8'))
    except ConnectionResetError:
        print(f"Connection lost with {username}.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if username:
            with lock:
                del clients[username]  # Remove the client from the dictionary on exit
            print(f"{username} has disconnected.")
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Server listening on port {PORT}...')

    while True:
        client_socket, client_address = server_socket.accept()
        print(f'Connection established with {client_address}')
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
