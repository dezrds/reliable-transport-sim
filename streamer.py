# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY

import struct
import time


class Streamer:
    def __init__(self, dst_ip, dst_port,
                 src_ip=INADDR_ANY, src_port=0):
        """Default values listen on all network interfaces, chooses a random source port,
           and does not introduce any simulated packet loss."""
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port

        #reciever
        self.expected_seq = 1         
        self.rec_buffer = {}         


        #sender
        self.send_seq_num = 0



    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        # Your code goes here!  The code below should be changed!
        len_bytes = len(data_bytes)
        bytes_sent = 0
        packet_size = 500
        chunk_begin = 0

        while bytes_sent < len_bytes:
            chunk = data_bytes[chunk_begin:chunk_begin+packet_size]
            chunk_size = len(chunk)
            self.send_seq_num += 1
            packed_data = struct.pack(f"iI500s", self.send_seq_num, chunk_size, chunk)
            self.socket.sendto(packed_data, (self.dst_ip, self.dst_port))
            chunk_begin += packet_size
            bytes_sent += packet_size

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""
        # your code goes here!  The code below should be changed!
        last_time = time.time()

        while True:
            if self.expected_seq in self.rec_buffer:
                payload_data = self.rec_buffer[self.expected_seq]
                del self.rec_buffer[self.expected_seq]
                self.expected_seq += 1
                return payload_data
            
            if time.time() - last_time > 1.5:
                return b''

            incoming_packet, addr = self.socket.recvfrom(508)
            seq_num, chunk_size = struct.unpack("iI", incoming_packet[:8])
            if seq_num == -1:
                self.final_seq = chunk_size
            else:
                payload_data = incoming_packet[8 : 8 + chunk_size]
                if seq_num >= self.expected_seq:
                    self.rec_buffer[seq_num] = payload_data

            


        return payload_data

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        pass
