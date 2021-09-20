'''
Universidad del Valle de Guatemala
Redes - CC3067
Proyecto 2

Integrantes:
- Luis Quezada 18028
- Jennifer Sandoval 18962
- Esteban del Valle 18221
'''

import json
import threading
import socket
import argparse


class Client:

	def __init__(self,server_host,server_port_tcp=1234,server_port_udp=1234,client_port_udp=1235):
		self.identifier = None
		self.server_message = []
		self.room_id = None
		self.client_udp = ("0.0.0.0", client_port_udp)
		self.lock = threading.Lock()
		self.server_listener = SocketThread(self.client_udp,self,self.lock)
		self.server_listener.start()
		self.server_udp = (server_host, server_port_udp)
		self.server_tcp = (server_host, server_port_tcp)
		self.register()

	def create_room(self, room_name=None):
		message = json.dumps({"action": "create", "payload": room_name, "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parse_data(data)
		self.room_id = message

	def join_room(self, room_id):
		self.room_id = room_id
		message = json.dumps({"action": "join", "payload": room_id, "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parse_data(data)
		self.room_id = message

	def autojoin(self):
		message = json.dumps({"action": "autojoin", "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parse_data(data)
		self.room_id = message

	def leave_room(self):
		message = json.dumps({"action": "leave","room_id": self.room_id,"identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parse_data(data)

	def get_rooms(self):
		message = json.dumps({"action": "get_rooms", "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parse_data(data)
		return message

	def send(self, message):
		message = json.dumps({
			"action": "send",
			"payload": {"message": message},
			"room_id": self.room_id,
			"identifier": self.identifier
		})
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(message.encode(), self.server_udp)

	def sendto(self, recipients, message):
		message = json.dumps({"action": "sendto","payload": {"recipients": recipients,"message": message},"room_id": self.room_id,"identifier": self.identifier})
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(message.encode(), self.server_udp)

	def register(self):
		message = json.dumps({"action": "register","payload": self.client_udp[1]})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parse_data(data)
		self.identifier = message

	def parse_data(self, data):
		try:
			data = json.loads(data)
			if data['success'] == "True":
				return data['message']
			else:
				raise Exception(data['message'])
		except ValueError:
			print(data)

	def get_messages(self):
		message = self.server_message
		self.server_message = []
		return set(message)


class SocketThread(threading.Thread):
	def __init__(self, addr, client, lock):
		threading.Thread.__init__(self)
		self.client = client
		self.lock = lock
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(addr)

	def run(self):
		while True:
			data, addr = self.sock.recvfrom(1024)
			self.lock.acquire()
			try:
				self.client.server_message.append(data)
			finally:
				self.lock.release()

	def stop(self):
		self.sock.close()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Simple game server')
	parser.add_argument('--tcpport',dest='tcp_port',help='Listening tcp port',default="1234")
	parser.add_argument('--udpport',dest='udp_port',help='Listening udp port',default="1234")
	parser.add_argument('--clientid',dest='client_id',help='Client game id',default="1235")

	args = parser.parse_args()

	client_id = int(args.client_id)
	client_port = int(args.tcp_port) + client_id

	#  Register on server
	client = Client("127.0.0.1",int(args.tcp_port),int(args.udp_port),client_port)

	try:
		client.autojoin()
	except Exception as e:
		print("Error : %s" % str(e))

	username = input(">> Enter your username: ")

	#  Main game loop
	while True:
		#  Send message to room (any serializable data)

		msgtext = input(">> Command: ")

		client.send({"name": username,"message": msgtext})

		print(client.get_rooms())

		msg = client.get_messages()
		if len(msg) != 0:
			for message in msg:
				message = json.loads(message)
				sender, value = message.popitem()
				print("%s: %s" % (value["name"], value["message"]))

	client.leave_room()

