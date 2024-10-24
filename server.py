import socket
import threading

clients = {}    # Stores username-socket key-pairs locally
lock = threading.Lock()

HOST = 'localhost'
PORT = int(input("Enter the port number to host the server on (e.g., 5555): "))

def authenticate(client_socket):
    client_socket.send(b'Welcome! Register or login: (R/L)')
    response = client_socket.recv(1024).decode('utf-8')
    
    if response.upper() == 'R':
        client_socket.send(b'Register')
        client_socket.send(b'Enter new username: ')
        username = client_socket.recv(1024).decode('utf-8')
        with lock:
            if username not in clients:
                clients[username] = client_socket
                client_socket.send(b'Registration successful! You can now login.')
            else:
                client_socket.send(b'Username already exists.')
                return
    elif response.upper() == 'L':
        client_socket.send(b'Login')
        client_socket.send(b'Enter your username: ')   
        username = client_socket.recv(1024).decode('utf-8')
        with lock:
            if username not in clients:
                clients[username] = client_socket
                client_socket.send(b'Username not found. Please register first.')
                return
            else:
                client_socket.send(b'Login successful!')
                return username

def handle_client(client_socket, client_address):
    try:
        username = authenticate(client_socket)
        client_socket.send(b'Choose a port number: ')
        port = client_socket.recv(1024).decode('utf-8')
        
        client_socket.send(b"Enter message (type 'exit' to quit): ")
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message.lower() == 'exit':
                break
            print(f"{username}: {message}")
            for sock in clients.values():
                if sock != client_socket:
                    sock.send(f"{username}: {message}".encode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
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

    
    
        
        
        
        
        
                    
            
                
            
        
        
