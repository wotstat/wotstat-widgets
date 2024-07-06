import socket
import struct

def read_frame(sock):
    # Read the width, height, and length (each 4 bytes)
    width_bytes = sock.recv(4)
    if not width_bytes:
        return None, None, None, None
    
    height_bytes = sock.recv(4)
    if not height_bytes:
        return None, None, None, None
    
    length_bytes = sock.recv(4)
    if not length_bytes:
        return None, None, None, None
    
    # Unpack the bytes to integers
    width = struct.unpack('!I', width_bytes)[0]
    height = struct.unpack('!I', height_bytes)[0]
    length = struct.unpack('!I', length_bytes)[0]
    
    # Read the data of the specified length
    data = sock.recv(length)
    if not data:
        return None, None, None, None
    
    return width, height, length, data

def main():
    host = 'localhost'  # Replace with the server's address
    port = 12345        # Replace with the server's port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print("Connected to server.")
        
        while True:
            width, height, length, data = read_frame(sock)
            if width is None or height is None or length is None:
                print("Disconnected from server.")
                break
            
            print(f"{width} x {height} ({length})")

if __name__ == "__main__":
    main()