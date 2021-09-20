'''
Universidad del Valle de Guatemala
Redes - CC3067
Proyecto 2

Integrantes:
- Luis Quezada 18028
- Jennifer Sandoval 18962
- Esteban del Valle 18221
'''

import uuid
import json
import socket


class Player:

    def __init__(self, addr, udp_port):
        self.identifier = str(uuid.uuid4())
        self.addr = addr
        self.udp_addr = (addr[0], int(udp_port))

    def send_tcp(self, success, data, sock):
        success_string = "False"
        if success:
            success_string = "True"
        message = json.dumps({"success": success_string, "message": data})
        sock.send(message.encode())

    def send_udp(self, player_identifier, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps({player_identifier: message}).encode(), self.udp_addr)
