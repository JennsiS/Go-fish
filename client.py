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
from game import Game
import time
import sys


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

	def createRoom(self, room_name=None):
		message = json.dumps({"action": "create", "payload": room_name, "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parseData(data)
		self.room_id = message

	def joinRoom(self, room_id):
		self.room_id = room_id
		message = json.dumps({"action": "join", "payload": room_id, "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parseData(data)
		self.room_id = message

	def autojoin(self):
		message = json.dumps({"action": "autojoin", "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parseData(data)
		self.room_id = message

	def leaveRoom(self):
		message = json.dumps({"action": "leave","room_id": self.room_id,"identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parseData(data)

	def getRooms(self):
		message = json.dumps({"action": "get_rooms", "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parseData(data)
		return message

	def send(self, message):
		message = json.dumps({"action": "send","payload": {"message": message},"room_id": self.room_id,"identifier": self.identifier})
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendTo(message.encode(), self.server_udp)

	def sendTo(self, recipients, message):
		message = json.dumps({"action": "sendto","payload": {"recipients": recipients,"message": message},"room_id": self.room_id,"identifier": self.identifier})
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendTo(message.encode(), self.server_udp)

	def register(self):
		message = json.dumps({"action": "register","payload": self.client_udp[1]})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parseData(data)
		self.identifier = message

	def parseData(self, data):
		try:
			data = json.loads(data)
			if data['success'] == "True":
				return data['message']
			else:
				raise Exception(data['message'])
		except ValueError:
			print(data)

	def getMessages(self):
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
	parser.add_argument('--id',dest='client_id',help='Client game id',default="1")

	args = parser.parse_args()

	# Setup id and client port
	client_id = int(args.client_id)
	client_port = int(args.tcp_port) + client_id

	#  Register on server
	client = Client("127.0.0.1",int(args.tcp_port),int(args.udp_port),client_port)

	try:
		# Join client to available room
		client.autojoin()
	except Exception as e:
		print("<!> Could not autojoin,",e)

	username = input(">> Enter your username: ")

	# Wait for room to fill
	rooms = client.getRooms()
	connectedPlayers = rooms[0]["nb_players"]
	maxPlayers = rooms[0]["capacity"]

	while connectedPlayers < maxPlayers:
		print("\n>> Waiting for other players to start game... (",connectedPlayers,"/",maxPlayers,")\n",sep="")
		time.sleep(3)
		rooms = client.getRooms()
		connectedPlayers = rooms[0]["nb_players"]
		maxPlayers = rooms[0]["capacity"]

	# Init game


	#  Main GAME loop
	continueLoop = True

	while continueLoop:
		msg = client.getMessages()
		if len(msg) != 0:
			for message in msg:
				message = json.loads(message)
				sender, value = message.popitem()
				print("[",value["name"],"]: ",value["message"],sep="")

		cmd = input("[chat/play/exit]: ")

		while cmd not in ["chat","play","exit"]:
			cmd = input("[chat/play/exit]: ")

		if cmd == "chat":
			msgtext = input("[chat msg]: ")
			client.send({"name": username,"message": msgtext})

		elif cmd == "play":
			# get game state and ask card or fish
			pass
			

		elif cmd == "exit":
			client.leaveRoom()
			print(">> Left room... disconnecting.")
			sys.exit()

