import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ATOM_IP = "192.168.97.216"

PORT = 5000

sock.sendto(b"MOVE 100 50", (ATOM_IP, PORT))