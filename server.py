'''
Universidad del Valle de Guatemala
Redes - CC3067
Proyecto 2

Integrantes:
- Luis Quezada 18028
- Jennifer Sandoval 18962
- Esteban del Valle 18221
'''

import argparse
import socket
import json
import time
from threading import Thread, Lock
from rooms import Rooms, RoomNotFound, NotInRoom, RoomFull


#Main Game loop for game logic
def main_loop(tcp_port, udp_port, rooms):
	lock = Lock()
	udp_server = UdpServer(udp_port, rooms, lock)
	tcp_server = TcpServer(tcp_port, rooms, lock)
	udp_server.start()
	tcp_server.start()
	is_running = True

	print("\n\n||==================================================||")
	print("\t\tAVAILABLE COMMANDS")
	print("||==================================================||")
	print("\n    [list] \t\t- list rooms")
	print("    [clear] \t\t- drop all rooms")
	print("    [roomstate <id>] \t- print room game state")
	print("    [room <id>] \t- print room information")
	print("    [user <id>] \t- print user information")
	print("    [quit] \t\t- quit server")
	print("    [help] \t\t- shows available commands")
	print("||==================================================||\n\n")

	while is_running:
		cmd = input(">> Command: ")
		
		if cmd == "list":
			rms = rooms.rooms.items()

			if len(rms) == 0:
				print(">> No active rooms.\n")
			else:
				print(">> Rooms:")
				for room_id, room in rms:
					print("\t- ",room.name," [",len(room.players),"/",room.capacity,"]",sep="")

		elif cmd == "clear":
			print(">> Dropping all rooms.\n")
			rooms.rooms = {}
			rooms.players = {}

		elif cmd.startswith("roomstate "):
			try:
				id = cmd[10:]
				room = rooms.rooms[id]
				room.game.stateToString()
				
			except:
				print("\n<!> Error while getting room game info.")
				
		elif cmd.startswith("room "):
			try:
				id = cmd[5:]
				room = rooms.rooms[id]
				print("\t- ",room.name," [",len(room.players),"/",room.capacity,"]",sep="")
				print("\tPlayers:")
				for player in room.players:
					print("\t- [ user ",player.identifier," ]",sep="")
			except:
				print("\n<!> Error while getting room informations.")
				
		elif cmd.startswith("user "):
			try:
				player = rooms.players[cmd[5:]]
				print(player.identifier," : ",player.udp_addr[0],":",player.udp_addr[1])
			except:
				print("\n<!> Error while getting user informations.")
				
		elif cmd == "quit":
			print(">> Shutting down server.")
			udp_server.is_listening = False
			tcp_server.is_listening = False
			is_running = False

		elif cmd == "help":
			print("\n\n||==================================================||")
			print("\t\tAVAILABLE COMMANDS")
			print("||==================================================||")
			print("\n    [list] \t\t- list rooms")
			print("    [clear] \t\t- drop all rooms")
			print("    [roomstate <id>] \t- print room game state")
			print("    [room <id>] \t- print room information")
			print("    [user <id>] \t- print user information")
			print("    [quit] \t\t- quit server")
			print("    [help] \t\t- shows available commands")
			print("||==================================================||\n\n")

	udp_server.join()
	tcp_server.join()



class UdpServer(Thread):
	def __init__(self, udp_port, rooms, lock):
		Thread.__init__(self)
		self.rooms = rooms
		self.lock = lock
		self.is_listening = True
		self.udp_port = int(udp_port)
		self.msg = '{"success": %(success)s, "message":"%(message)s"}'

	def run(self):
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.sock.bind(("0.0.0.0", self.udp_port))
		self.sock.setblocking(0)
		self.sock.settimeout(5)
		while self.is_listening:
			try:
				data, address = self.sock.recvfrom(1024)
			except socket.timeout:
				continue

			try:
				data = json.loads(data)
				try:
					identifier = data['identifier']
				except KeyError:
					identifier = None

				try:
					room_id = data['room_id']
				except KeyError:
					room_id = None

				try:
					payload = data['payload']
				except KeyError:
					payload = None

				try:
					action = data['action']
				except KeyError:
					action = None

				try:
					if room_id not in self.rooms.rooms.keys():
						raise RoomNotFound
					
					self.lock.acquire()
					
					try:
						if action == "send":
							try:
								self.rooms.send(identifier,room_id,payload['message'],self.sock)
							except:
								pass
						elif action == "sendto":
							try:
								self.rooms.sendto(identifier,room_id,payload['recipients'],payload['message'],self.sock)
							except:
								pass
							
					finally:
						self.lock.release()
						
				except RoomNotFound:
					print("<!> Room not found.")

			except KeyError:
				print("<!> Json from ",address," is not valid.")
				
			except ValueError:
				print("<!> Message from ",address," is not valid json string.")

		self.stop()
		

	def stop(self):
		self.sock.close()


class TcpServer(Thread):
	def __init__(self, tcp_port, rooms, lock):
		Thread.__init__(self)
		self.lock = lock
		self.tcp_port = int(tcp_port)
		self.rooms = rooms
		self.is_listening = True
		self.msg = '{"success": "%(success)s", "message":"%(message)s"}'

	def run(self):
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.bind(('0.0.0.0', self.tcp_port))
		self.sock.setblocking(0)
		self.sock.settimeout(5)
		time_reference = time.time()
		self.sock.listen(1)

		while self.is_listening:

			if time_reference + 60 < time.time():
				self.rooms.remove_empty()
				time_reference = time.time()
			try:
				conn, addr = self.sock.accept()
				
			except socket.timeout:
				continue

			data = conn.recv(1024)
			
			try:
				data = json.loads(data)
				action = data['action']
				identifier = None
				try:
					identifier = data['identifier']
				except KeyError:
					pass 

				room_id = None
				
				try:
					room_id = data['room_id']
				except KeyError:
					pass 

				payload = None
				
				try:
					payload = data['payload']
				except KeyError:
					pass

				game = None
				
				try:
					game = data['game']
				except KeyError:
					pass
				
				self.lock.acquire()
				
				try:
					self.route(conn,addr,action,payload,identifier,room_id,game)
				finally:
					self.lock.release()
					
			except KeyError:
				print("<!> Json from ",addr," is not valid.")
				conn.send("<!> Json is not valid.")
				
			except ValueError:
				print("<!> Message from ",addr," is not valid json string.")
				conn.send("<!> Message is not a valid json string.")

			conn.close()

		self.stop()

	def route(self,sock,addr,action,payload,identifier=None,room_id=None,game=None):
		if action == "register":
			client = self.rooms.register(addr, int(payload))
			client.send_tcp(True, client.identifier, sock)
			return 0

		if identifier is not None:
			if identifier not in self.rooms.players.keys():
				print("\n<!> Unknown identifier ",identifier," for ",addr[0],":",addr[1])
				sock.send(self.msg % {"success": "False", "message": "Unknown identifier"})
				return 0

			client = self.rooms.players[identifier]

			if action == "join":
				try:
					if payload not in self.rooms.rooms.keys():
						raise RoomNotFound()
					self.rooms.join(identifier, payload)
					client.send_tcp(True, payload, sock)
					
				except RoomNotFound:
					client.send_tcp(False, room_id, sock)
					
				except RoomFull:
					client.send_tcp(False, room_id, sock)

			elif action == "get_game":
				try:
					if payload not in self.rooms.rooms.keys():
						raise RoomNotFound()
					gameData = self.rooms.get_game(payload)
					client.send_tcp(True, gameData, sock)
				except:
					print("\n<!> Error getting game.")

			elif action == "set_game":
				try:
					if payload not in self.rooms.rooms.keys():
						raise RoomNotFound()
					self.rooms.set_game(payload,game)
					client.send_tcp(True, payload, sock)
				except:
					print("\n<!> Error setting game.")

			elif action == "room_ready":
				try:
					if payload not in self.rooms.rooms.keys():
						raise RoomNotFound()
					is_ready = self.rooms.is_ready(payload)
					client.send_tcp(True, is_ready, sock)
				except:
					print("\n<!> Error in checking if room ready.")

			elif action == "get_client_game_id":
				try:
					if payload not in self.rooms.rooms.keys():
						raise RoomNotFound()
					client_game_id = self.rooms.get_client_game_id(payload,identifier)
					client.send_tcp(True, client_game_id, sock)
				except:
					print("\n<!> Error getting client game id.")
					
			elif action == "autojoin":
				room_id = self.rooms.join(identifier)
				client.send_tcp(True, room_id, sock)
				
			elif action == "get_rooms":
				rooms = []
				for id_room, room in self.rooms.rooms.items():
					rooms.append({"id": id_room,"name": room.name,"connected_players": len(room.players),"capacity": room.capacity})
					
				client.send_tcp(True, rooms, sock)
				
			elif action == "create":
				room_identifier = self.rooms.create(payload)
				self.rooms.join(client.identifier, room_identifier)
				client.send_tcp(True, room_identifier, sock)
				
			elif action == 'leave':
				try:
					if room_id not in self.rooms.rooms:
						raise RoomNotFound()
					self.rooms.leave(identifier, room_id)
					client.send_tcp(True, room_id, sock)
					
				except RoomNotFound:
					client.send_tcp(False, room_id, sock)
					
				except NotInRoom:
					client.send_tcp(False, room_id, sock)
			else:
				sock.send_tcp(self.msg % {"success": "False","message": "You must register"})
				

	def stop(self):
		self.sock.close()

if __name__ == "__main__":

        #Set ports
	parser = argparse.ArgumentParser(description='Simple game server')
	parser.add_argument('--tcpport',dest='tcp_port',help='Listening tcp port',default="1234")
	parser.add_argument('--udpport',dest='udp_port',help='Listening udp port',default="1234")
	parser.add_argument('--capacity',dest='room_capacity',help='Max players per room',default="3")

        #Create rooms and run game loop
	args = parser.parse_args()
	rooms = Rooms(int(args.room_capacity))
	main_loop(args.tcp_port, args.udp_port, rooms)




