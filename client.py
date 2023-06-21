import socket
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

# Configuration
PROXY_HOST = '127.0.0.2'
PROXY_PORT = 9000
BUFFER_SIZE = 4096
SESSION_KEY = b'your_session_key'
IV = b'aaaaaaaaaaaaaaaa'
file_name='max.rar'

def encrypt(data):
    cipher = AES.new(SESSION_KEY, AES.MODE_CBC, IV)
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))
    return encrypted_data


def decrypt(data):
    cipher = AES.new(SESSION_KEY, AES.MODE_CBC, IV)
    decrypted_data = unpad(cipher.decrypt(data), AES.block_size)
    return decrypted_data


def download_file(file_name):
    # Create a socket for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((PROXY_HOST, PROXY_PORT))

    # Create a GET request for the file
    request = f"GET /{file_name} HTTP/1.1\r\nHost: {PROXY_HOST}\r\n\r\n"

    # Send the request to the proxy server
    client_socket.send(request.encode())
    print("Request sent to proxy server...")

    # Receive the response from the proxy server
    response = b""
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            break
        response += data

    # Decrypt the response
    decrypted_response = decrypt(response)

    # Save the file locally
    with open(file_name, 'wb') as file:
        file.write(decrypted_response)

    client_socket.close()
    print("File downloaded successfully.")


# Usage example
download_file('max.rar')
