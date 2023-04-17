import socket
import hashlib
import time

PROX1_IP = "10.9.0.3"
PROXY1_PORT = 12345
PROXY1_PORT_UDP = 30210
PROX2_IP = "10.9.0.4"
PROXY2_PORT = 54321
PROXY2_PORT_TCP = 33333
RECEIVER_IP = "10.9.0.5"
RECEIVER_PORT = 22222
if __name__ == '__main__':
    # data for opening sockets
    addr = '0.0.0.0'  # just till he will get the first chunk of the image
    # buffer_size = 17000
    buffer_size = 6000
    # Create a UDP socket and bind it to the specified IP address and port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # ipv4, udp socket
    sock.bind((PROX2_IP, PROXY2_PORT))
    print("proxy2 is on...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', PROXY2_PORT_TCP))
    s.listen(2)
    sock.setblocking(False)  # socket not blocking for timeout
    # time.sleep(15)  # wait for app to get path from server
    # Open a file to write the received chunks to
    firstime = True
    while 1:
        # count = 0
        with open("proxy2", "wb") as f:
            wanted_seq = 0
            # Receive and write each chunk to the file
            while True:
                num = 5  # for timeout
                data = 0
                print("wait to recv..")
                # socket_name = sock.getsockname()
                # print(f"Socket bound to port {socket_name[1]}")

                # try to get the chunk fot 5 seconds
                while num:
                    # print("num = ", num)
                    try:
                        data, addr = sock.recvfrom(buffer_size)
                        # print("addr: ", addr)
                        # print("data: ", data)
                    except socket.error:
                        # print("didn't received data")
                        # no data available to receive
                        pass
                    time.sleep(1)  # timeout
                    num -= 1
                    if data:
                        seq = (str(data)).split("seq!!!!!")[0]
                        # print("seq=", seq)
                        if seq == "b'final'":
                            break
                        # print("data before: ", data)
                        # print("what we remove: ", data[:(len(seq) - 2) + len("seq!!!!!")])
                        data = data[(len(seq) - 2) + len("seq!!!!!"):]
                        # print("data after: ", data)
                        seq = seq.replace("seq!!!!!", "").replace("b'", "").replace('b"', "")
                        seq = int(seq)
                        print("got packet seq:", seq)
                        # print("data =", data)
                        # seq from packet is equal to the number we need to get
                        if seq == wanted_seq:
                            # write data to file
                            f.write(data)
                            wanted_seq += 1
                            # count = 0
                        else:
                            # count += 1
                            pass
                        break
                # in the last packet, after all the image was send we got a final message
                if data == b'final':
                    print("got all the file!")
                    break
                # send the ack
                ack_re = "ack:" + str(wanted_seq - 1)
                if addr != '0.0.0.0' and addr[1] == 30210:
                    # print("addr: ", addr)
                    sock.sendto(ack_re.encode(), addr)
                    print("send seq: ", wanted_seq - 1)
                    # print("ack_re", ack_re)
        with open("proxy2", 'rb') as f:
            data = f.read()
            size = len(data)
            md5_created = hashlib.md5(data).hexdigest()
            print(md5_created)
        # if firstime:
        # # tcp to receiver
        #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     s.bind(('0.0.0.0', PROXY2_PORT_TCP))
        #     s.listen(2)
        #     firstime = False
        # Connect to the server
        # s.connect((RECEIVER_IP, RECEIVER_PORT))
        # Wait for a client to connect
        conn, addr = s.accept()
        print("sending file to receiver")
        conn.send(str(size).encode())
        with open("proxy2", 'rb') as f:
            # print("file len: ", file_length)
            while 1:
                # Read a chunk of data from the file
                data = f.read(4096)
                time.sleep(0.5)
                # If there's no more data, break out of the loop
                if not data:
                    break
                # Send the chunk of data over the socket
                conn.send(data)
            print("done with receiver")
            # s.close()

        # sock.close()






