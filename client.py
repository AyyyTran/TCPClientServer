import socket

def start_client(target_ip, target_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        message = input("Enter message to send: ")
        if not message:
            break

        client_socket.sendto(message.encode(), (target_ip, target_port))

        try:
            client_socket.settimeout(2)  # 2-second timeout
            ack_message, server_address = client_socket.recvfrom(1024)
            print(f"Acknowledgment from server: {ack_message.decode()}")
        except socket.timeout:
            print("No acknowledgment received. Timeout!")

if __name__ == "__main__":
    start_client("127.0.0.1", 5000)
