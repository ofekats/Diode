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
    buffer_size = 10000
    addr = '0.0.0.0'
    # Create a UDP socket and bind it to the specified IP address and port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # ipv4, udp socket
    sock.bind((PROX2_IP, PROXY2_PORT))
    print("proxy2 is on...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', PROXY2_PORT_TCP))
    s.listen(2)
    sock.setblocking(False)  # socket not blocking for packet lost
    # Open a file to write the received chunks to
    notproxy1 = False
    firstime = True
    while 1:
        with open("proxy2", "wb") as f:
            wanted_seq = 0
            # Receive and write each chunk to the file
            while True:
                num = 5  # for packet lost
                data = 0
                print("wait to recv..")
                # try to get the chunk fot 5 seconds
                while num:
                    try:
                        data, addr = sock.recvfrom(buffer_size)
                    except socket.error:
                        # no data available to receive
                        pass
                    time.sleep(0.5)  # for packet lost
                    num -= 1
                    if data:
                        # special word that if proxy2 doesn't get he won't get the file
                        seq = str(data).split("seq!!!!!")[0]
                        if seq == "b'final'":
                            break
                        data = data[(len(seq) - 2) + len("seq!!!!!"):]
                        seq = seq.replace("seq!!!!!", "").replace("b'", "").replace('b"', "")
                        try:
                            seq = int(seq)
                        except ValueError:
                            notproxy1 = True
                            print("not proxy1!!!")
                            break
                        print("got packet seq:", seq)
                        # seq from packet is equal to the number we need to get
                        if seq == wanted_seq:
                            # write data to file
                            f.write(data)
                            notproxy1 = False
                            wanted_seq += 1
                        break
                # in the last packet, after all the image was send we got a final message
                if notproxy1:
                    break
                if data == b'final':
                    print("got all the file!")
                    break
                # send the ack
                ack_re = "ack:" + str(wanted_seq - 1)
                if addr[0] == PROX1_IP and addr[1] == 30210:  # only proxy1 IP and PORT
                    sock.sendto(ack_re.encode(), addr)
                    print("send seq: ", wanted_seq - 1)
        if not notproxy1:
            with open("proxy2", 'rb') as f:
                data = f.read()
                size = len(data)
                md5_created = hashlib.md5(data).hexdigest()
                print(md5_created)
            # Wait for a client to connect
            conn, addr = s.accept()
            print("sending file to receiver")
            conn.send(str(size).encode())
            with open("proxy2", 'rb') as f:
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






