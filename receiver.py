import socket
import hashlib
import time

PROX2_IP = "10.9.0.4"
PROXY2_PORT_TCP = 33333
RECEIVER_IP = "10.9.0.5"
RECEIVER_PORT = 22222
if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # time.sleep(30)
    # Connect to the server
    s.connect((PROX2_IP, PROXY2_PORT_TCP))
    print("receiver ready to get data")
    size = s.recv(80)
    size = size.decode("UTF-8");
    file_len = int(size)
    with open("receiver", 'wb') as f:
        i = 0
        while file_len > 0:
            print("in while: ", i)
            i += 1
            print("size =", file_len)
            # Receive a chunk of data from the socket
            data = s.recv(1024)
            # If there's no more data, break out of the loop
            if not data:
                break
            file_len -= 1024
            f.write(data)
    print("receiver got all the file!")
    with open("receiver", 'rb') as f:
        data = f.read()
        md5_created = hashlib.md5(data).hexdigest()
        print(md5_created)
