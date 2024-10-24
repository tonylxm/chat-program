import socket

HOST = 'localhost'
PORT = 5555

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    while True:
        server_message = client_socket.recv(1024).decode('utf-8')
        print(server_message)
        
        if server_message.startswith(">>"):
            message = input("You: ")
            if message.lower() == 'exit':
                client_socket.send(message.encode('utf-8'))
                break
            client_socket.send(message.encode('utf-8'))
    
    client_socket.close()

if __name__ == "__main__":
    start_client()            
        
    
    