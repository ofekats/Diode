import socket
import hashlib
from tqdm import tqdm
from time import sleep

PROX1_IP = "10.9.0.3"
PROXY1_PORT = 12345
SENDER_IP = "10.9.0.2"
if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    s.connect((PROX1_IP, PROXY1_PORT))
    filename = "sunflower.jpeg"
    with open(filename, 'rb') as f:
        data = f.read()
        file_length = len(data)
        md5 = hashlib.md5(data).hexdigest()
    print("file MD5: ", md5)
    print("sending the file...")
    buffer_size = 4096
    with open(filename, 'rb') as f:
        num = int(file_length/buffer_size)+1
        for i in tqdm(range(num)):
            # Read a chunk of data from the file
            data = f.read(buffer_size)
            sleep(0.2)
            # If there's no more data, break out of the loop
            if not data:
                break
            # Send the chunk of data over the socket
            s.send(data)
