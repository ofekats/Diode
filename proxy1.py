import socket
import hashlib
import time

PROX1_IP = "10.9.0.3"
PROXY1_PORT_TCP = 12345
PROXY1_PORT_UDP = 30210
PROX2_IP = "10.9.0.4"
PROXY2_PORT = 54321
if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(('0.0.0.0', PROXY1_PORT_TCP))
    s.listen(2)
    print("proxy1 is listening...")
    firstime = True
    while 1:
        # Wait for a client to connect
        conn, addr = s.accept()
        with conn:
            print(f'Connected by {addr}')

            # Receive data from the client
            # md5_received = conn.recv(128)
            # print(f'Received data: {md5_received}')
            with open("proxy1", 'wb') as f:
                while True:
                    # Receive a chunk of data from the socket
                    data = conn.recv(4096)

                    # If there's no more data, break out of the loop
                    if not data:
                        break
                    f.write(data)
            with open("proxy1", 'rb') as f:
                data = f.read()
                md5_created = hashlib.md5(data).hexdigest()
                print(md5_created)
        # if md5_received.decode("UTF-8") == md5_created:
        #     print("file received (:")
        # else:
        #     print("not good")



        #rudp
        # Define the IP address and port number of the receiver
        # buffer_size = 16024  # the min window sent
        buffer_size = 4096  # the min window sent
        # Open the image file in binary mode
        with open("proxy1", "rb") as f:
            # Create a UDP socket
            if firstime:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((PROX1_IP, PROXY1_PORT_UDP))
                sock.setblocking(False)  # socket not blocking for timeout
                firstime = False
            socket_name = sock.getsockname()
            print(f"Socket bound to port {socket_name[1]}")
            # Read the image file in chunks and send them over UDP
            seq_num = 0
            seq_ack = -1
            while True:
                if seq_num == (seq_ack + 1):  # if we got ack send new data
                    chunk = f.read(buffer_size)
                    # print("data: ", chunk)
                    print("send new packet")
                    if not chunk:
                        # End of file reached
                        print("no more data to send")
                        break
                # Send the chunk over UDP
                proxy2 = (PROX2_IP, PROXY2_PORT)
                seq_data = str(seq_num) + "seq!!!!!"
                sock.sendto(seq_data.encode() + chunk, proxy2)
                print("seq_num", seq_num)
                num = 5  # for timeout
                data = False
                print("wait for ack")
                while num:
                    # print("num = ", num)
                    try:
                        data, addr = sock.recvfrom(80)
                        # print("data = ", data)
                    except socket.error:
                        # No data available to receive
                        pass
                    time.sleep(1)  # timeout
                    num -= 1
                    if data:
                        seq_ack = (data.decode("utf-8")).split("ack:")[1].split("'")[0]
                        seq_ack = int(seq_ack)
                        print("ack seq:", seq_ack)
                        if seq_num == seq_ack:
                            print("got ack!")
                            seq_num += 1
                        elif seq_num != seq_ack:
                            print("\ntimeout!!!")
                        break

                if not data:
                    print("didn't recv")

            # after we sent all the data, send to client final message
            chunk = "final"
            sock.sendto(chunk.encode(), proxy2)
            # Close the socket
            # sock.close()
            print("done with proxy2")

    # s.close()





