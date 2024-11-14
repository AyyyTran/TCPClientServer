import socket

def start_server(listen_ip, listen_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((listen_ip, listen_port))
    print(f"Server listening on {listen_ip}:{listen_port}")

    while True:
        message, client_address = server_socket.recvfrom(1024)  # buffer size 1024 bytes
        print(f"Received message: {message.decode()} from {client_address}")
        
        ack_message = "ACK"
        server_socket.sendto(ack_message.encode(), client_address)

if __name__ == "__main__":
    start_server("0.0.0.0", 5000)
