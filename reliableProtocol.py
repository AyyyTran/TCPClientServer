import socket
import sys
from customPacket import CustomPacket
class ReliableProtocol:

    def __init__(self):
        self.packets = []

    def connect(self, client_socket, target_ip, taget_port_num, timeout_in_secs):
        timeout_limit = 10
        counter = 0
        sequence_num = 0
        while True:
            if (counter == timeout_limit):
                print("\nLimit reached for attempting accept. Closing client connection...")
                client_socket.close()
                sys.exit("Client socket closed. Exiting...")
            try:
                print("sending connect")
                self.send(client_socket, "",sequence_num,  target_ip, taget_port_num)
                client_socket.settimeout(timeout_in_secs) 
                flag, seq_num, message, sender_address  = self.recieve(client_socket)
                packet_added = self.packet_added(flag, seq_num, message)
                if packet_added:
                    if flag == "ACK":
                        print("connection established")
                        packet = CustomPacket(seq_num)
                        packet_payload = packet.create_payload(message)
                        break
            except socket.timeout:
                print("No acknowledgment received. Timeout!")
                self.send(client_socket, "",sequence_num,  target_ip, taget_port_num)
                counter+=1

            

    def accept(self):
        print("SYN packet recieved")
        if self.packets and self.packets[-1].sequence_num != 0:
            self.packets.clear()
        

   
    def send(self, socket,message,seq_num,target_ip_addr, target_port_num = None):
        MAX_PACKET_SIZE = 1400  
        truncated_message = message[:MAX_PACKET_SIZE] if len(message) > MAX_PACKET_SIZE else message
        
        packet = CustomPacket(seq_num)
        packet_payload = packet.create_payload(truncated_message)
        encoded_payload = packet_payload.encode()
        target_info = target_ip_addr
        if target_port_num:
            target_info = (target_ip_addr, target_port_num) 
        socket.sendto(encoded_payload, target_info)

        if message:
            if len(message) > MAX_PACKET_SIZE:
                print(f"Sent truncated message: {truncated_message} (first {MAX_PACKET_SIZE} bytes)")
            else:
                print(f"Sent full message: {message}")

 
    def recieve(self, socket):
        byte_payload, sender_address = socket.recvfrom(1024)
        packet_payload = byte_payload.decode()
        flag,seq_num, message = CustomPacket.unpack_packet(packet_payload)
        return flag,seq_num, message, sender_address
        
    def packet_added(self, flag,seq_num, message):
        packet = CustomPacket(seq_num)
        packet_payload = packet.create_payload(message)
        if self.packets and (packet.sequence_num == self.packets[-1].sequence_num):
            return False
        else:
            self.packets.append(packet)
            return True
