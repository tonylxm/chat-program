import socket

HOST = 'localhost'
PORT = 5555

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    try:
        while True:
            server_message = client_socket.recv(1024).decode('utf-8')
            if not server_message:
                print("Connection closed by the server.")
                break
            print(server_message)

            message = input(">> ").strip()
            if not message:
                print("Empty input, please try again.")
                continue
            if message.lower() == 'exit':
                client_socket.send(message.encode('utf-8'))
                break
            client_socket.send(message.encode('utf-8'))
    except ConnectionResetError:
        print("Connection lost.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()