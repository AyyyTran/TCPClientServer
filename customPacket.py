

class CustomPacket:
    def __init__(self, seq_num, ack_num):
        self.flags = ["SYN", "ACK", "FIN", "RST"]
        # self.header = {"seqnum": 0, "acknum" : 0}
        self.sequence_num = seq_num
        self.acknowledgment_num = ack_num
        self.header = ""

    def create_header(self):
        # sequence_num = self.header["seqnum"]
        # acknowledgment_num = self.header["acknum"]
        flag = ""
        if self.sequence_num < 1 :
            flag = self.flags[0]
        else:
            flag = self.flags[2]
        self.header =  flag + "Seq:" +  str(self.sequence_num) + "Ack:" + str(self.acknowledgment_num)
    
    def create_packet_payload(self, message):
        payload =  self.header + message
        return payload