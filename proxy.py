import socket
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

# Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 8000
PROXY_HOST = '127.0.0.2'
PROXY_PORT = 9000
BUFFER_SIZE = 4096
SESSION_KEY = b'your_session_key'
IV = b'aaaaaaaaaaaaaaaa'

# Create a socket for the proxy server
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy_socket.bind((PROXY_HOST, PROXY_PORT))
proxy_socket.listen(5)

print(f"Proxy server is listening on {PROXY_HOST}:{PROXY_PORT}")


def encrypt(data):
    cipher = AES.new(SESSION_KEY, AES.MODE_CBC, IV)
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))
    return encrypted_data


def decrypt(data):
    cipher = AES.new(SESSION_KEY, AES.MODE_CBC, IV)
    decrypted_data = unpad(cipher.decrypt(data), AES.block_size)
    return decrypted_data


def handle_client(client_socket):
    print("Handling client request...")
    request = client_socket.recv(BUFFER_SIZE)
    # Authenticate client (You can implement your own authentication logic here)
    if not authenticate(request):
        client_socket.send(b"Authentication failed.")
        client_socket.close()
        return

    # Extract the file name from the request
    first_line = request.decode().split('\r\n')[0]
    file_name = first_line.split()[1].lstrip('/')
    print(f"Requested file: {file_name}")

    # Forward the request to the file server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((SERVER_HOST, SERVER_PORT))
    server_socket.send(request)

    # Receive response from the file server
    response = b""
    while True:
        data = server_socket.recv(BUFFER_SIZE)
        if not data:
            break
        response += data

    # Encrypt the response before sending it back to the client
    encrypted_response = encrypt(response)

    # Send the encrypted response to the client
    client_socket.sendall(encrypted_response)

    server_socket.close()
    client_socket.close()
    print("Request handled successfully.")


def authenticate(request):
    # Implement your authentication logic here
    # Return True if authentication succeeds, False otherwise
    return True


# Main proxy server loop
while True:
    client_socket, client_address = proxy_socket.accept()
    print(f"New connection from {client_address[0]}:{client_address[1]}")
    handle_client(client_socket)
