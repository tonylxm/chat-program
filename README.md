# SOFTENG 364 Assignment 2 - Chat Program

## Overview
This project implements a 1-1 chatting program using Python. It consists of a client and a server, allowing users to register, login, and chat securely. The connection between the server and client is encrypted using SSL/TLS.

## Requirements
- Python 3.7 or above
- OpenSSL

## Installation Instructions

### 1. Clone the Repository
To get the project files, clone the repository using the following command:

```bash
git clone https://github.com/tonylxm/chat-program
```

### 2. Install Dependencies
Navigate to the project directory and install the required dependencies. If you don't have pip installed, you can download it from pip's official website.

```bash
cd chat-program
pip install pyopenssl
```

#### Set up OpenSSL
You need to generate a self-signed SSL/TLS certificate and a private key to enable secure communication between the server and client. Follow these steps:

Make sure you have OpenSSL installed on your machine. You can verify the installation by running:

```bash
openssl version
```

If OpenSSL is not installed, you can install it using the package manager of your operating system.

For example:

Ubuntu/Debian:
```bash
sudo apt-get install openssl
```

macOS (using Homebrew):
```bash
brew install openssl
```

Windows: Download and install OpenSSL from the [official OpenSSL website](https://openssl-library.org/source/).

1. Generate a private key file

    ```bash
    openssl genpkey -algorithm RSA -out cert.key -aes256
    ```

2. Generate a certificate signing request (CSR) file

    ```bash
    openssl req -new -key cert.key -out cert.csr
    ```

3. Generate a self-signed certificate file

    ```bash
    openssl x509 -req -days 365 -in cert.csr -signkey cert.key -out cert.pem
    ```

Ensure that the following files are created in the project directory:

- cert.key (private key)
- cert.csr (certificate signing request)
- cert.pem (self-signed certificate)

### How to run the chat program
**1. Start the server first**
```bash
python3 server.py
```
You should see a message indicating that the secure server is waiting for connections.

**2. Run the clients**

Open a new terminal window (or tab) for each client and run the client script:

```bash
python3 client.py
```
Repeat this step for as many clients as you wish to test (e.g., two clients for a 1-1 chat).

**3. Client Instructions**

Once the client is running, follow the instructions displayed in the terminal:

- Register: Type R to register a new account. You will be prompted to choose a username and password.
- Login: Type L to log in with an existing username and password.
- Chat: After successful authentication, you can start chatting with the connected client.

**4. Stop chatting by typing 'exit'**
