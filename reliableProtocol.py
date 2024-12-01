import socket
import sys
from customPacket import CustomPacket
class ReliableProtocol:
# Protocol class to manage packets
    def __init__(self):
        self.packets = []
        # self.sequence_num = 0
        # self.sequence_num = 0

    def connect(self, client_socket, target_ip, taget_port_num, timeout_in_secs):
        # packet = CustomPacket(sequence_num, sequence_num)
        # packet.create_header()
        # packet_payload = packet.create_packet_payload(message)
        # socket.sendto(packet_payload.encode(), (target_ip, taget_port_num))
        # self.packets.append(packet)

        # Yep so basically I made a function in sutom protocol to create the packet instead
        # And then now Im using custom send and recieve functions in this class
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
                    # flag = message[0:3]
                    # self.sequence_num += 1
                    if flag == "ACK":
                    #     print("Server responded with ACK")
                        # ack += 1
                        print("connection established")
                        packet = CustomPacket(seq_num)
                        packet_payload = packet.create_payload(message)
                        break
            except socket.timeout:
                print("No acknowledgment received. Timeout!")
                self.send(client_socket, "",sequence_num,  target_ip, taget_port_num)
                counter+=1
                print("Resending connect ")
            

    def accept(self):
        print("SYN packet recieved")
        if self.packets and self.packets[-1].sequence_num != 0:
            self.packets.clear()
        

   
    def send(self, socket,message,seq_num,target_ip_addr, target_port_num = None):
        # packet = CustomPacket(self.sequence_num, self.sequence_num)
        # print("sending " + message + str(ack))
        MAX_PACKET_SIZE = 1400  # Define the max packet size
        truncated_message = message[:MAX_PACKET_SIZE] if len(message) > MAX_PACKET_SIZE else message
        
        packet = CustomPacket(seq_num)
        packet_payload = packet.create_payload(truncated_message)
        # print("sent packet: " + str(packet))
        # print("sent payload: " + packet_payload)
        encoded_payload = packet_payload.encode()
        target_info = target_ip_addr
        if target_port_num:
            target_info = (target_ip_addr, target_port_num) 
        socket.sendto(encoded_payload, target_info)
        # print("sent " + message + strz(encoded_payload))

        if message:
            if len(message) > MAX_PACKET_SIZE:
                print(f"Sent truncated message: {truncated_message} (first {MAX_PACKET_SIZE} bytes)")
            else:
                print(f"Sent full message: {message}")

 
    def recieve(self, socket):
        byte_payload, sender_address = socket.recvfrom(1024)
        packet_payload = byte_payload.decode()
        flag,seq_num, message = CustomPacket.unpack_packet(packet_payload)
        # print("recieved payload: " + packet_payload)
        return flag,seq_num, message, sender_address
        
    def packet_added(self, flag,seq_num, message):
        packet = CustomPacket(seq_num)
        packet_payload = packet.create_payload(message)
        # print(self.packets)
        if self.packets:
            print("Current: " + str(packet.sequence_num) + "Prev:" + str(self.packets[-1].sequence_num))
        if self.packets and (packet.sequence_num == self.packets[-1].sequence_num):
            # print("Duplicate packet with ack" + str(ack) + " ignoring")
            return False
        else:
            self.packets.append(packet)
            # print("Adding: " + str(packet_payload))
            # print(self.packets)
            return True
    def close(socket):
        socket.close()