
# packet class
class CustomPacket:
    def __init__(self, seq_num):
        self.flags = ["SYN", "ACK", "FIN"]
        # self.header = {"seqnum": 0, "acknum" : 0}
        # self.sequence_num = seq_num
        self.sequence_num = seq_num
        self.header = ""

    def create_header(self):
        # sequence_num = self.header["seqnum"]
        # sequence_num = self.header["acknum"]
        flag = ""
        # set the fin flag 
        if self.sequence_num == -1:
            flag = self.flag[2]
        # if self.sequence_num == 0: set syn packet
        if self.sequence_num == 0:
            flag = self.flags[0]
        else:
            # set ack packet 
            flag = self.flags[1]

        # self.header =  flag + "Seq:" +  str(self.sequence_num) + "Ack:" + str(self.sequence_num)
        self.header =  flag + "Seq:" + str(self.sequence_num)
    
    def create_payload(self, message):
        self.create_header()
        packet_payload =  self.header + "Msg:" + message
        return packet_payload
    
    def unpack_packet(payload):
        # flag_split_message = decoded_payload.split("Seq:")
        flag_split_message = payload.split("Seq:")
        flag = flag_split_message[0]
        seq_num = flag_split_message[1].split("Msg:")[0]
        message_split_string =  payload.split("Msg:")
        message = message_split_string[1]
        return flag,int(seq_num), message
