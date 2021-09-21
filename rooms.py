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
from player import Player

class Room:
	def __init__(self, identifier, capacity, room_name):
		self.capacity = capacity
		self.players = []
		self.identifier = identifier
		if room_name is not None:
			self.name = room_name
		else:
			self.name = self.identifier

	# Checking if the room is full (that the number of players is equal to the capacity of the room)
	def is_full(self):
		if len(self.players) == self.capacity:
			return True
		else:
			return False

	# Adding the players to the room
	def join(self, player):
		if not self.is_full():
			self.players.append(player)
		else:
			pass

	# Removing players who leave the room
	def leave(self, player):
		if player in self.players:
			self.players.remove(player)
		else:
			pass

	# Checking if the room is empty
	def is_empty(self):
		if len(self.players) == 0:
			return True
		else:
			return False

	# Checking if a specific player is inside the room
	def is_in_room(self, playerID):
		inRoom = False
		for player in self.players:
			if player.identifier == playerID:
				inRoom = True
				break
		return inRoom

class Rooms:
	def __init__(self, capacity=2):
		self.rooms = {}
		self.players = {}
		self.room_capacity = capacity

	# Register a new player
	def register(self, addr, udp_port):
		player = None
		for registered_player in self.players.values():
			if registered_player.addr == addr:
				player = registered_player
				player.udp_addr((addr[0], udp_port))
				break

		if player is None:
			player = Player(addr, udp_port)
			self.players[player.identifier] = player

		return player

	# Join a player to a room
	def join(self, playerID, roomId=None):
		if playerID not in self.players:
			raise ClientNotRegistered()

		player = self.players[playerID]

		if roomId is None:
			for roomId in self.rooms.keys():
				if not self.rooms[roomId].is_full():
					self.rooms[roomId].players.append(player)
					return roomId
					break
			roomId = self.create()
			self.join(playerID, roomId)
			return roomId

		elif roomId in self.rooms:
			if not self.rooms[roomId].is_full():
				self.rooms[roomId].players.append(player)
				return roomId
			else:
				raise RoomFull()
		else:
			pass

	# Remove a player from a room
	def leave(self, playerID, roomId):
		if playerID not in self.players:
			raise ClientNotRegistered()

		player = self.players[playerID]

		if roomId in self.rooms:
			self.rooms[roomId].leave(player)
		else:
			pass

	# Create a new room
	def create(self, room_name=None):
		identifier = str(uuid.uuid4())
		self.rooms[identifier] = Room(identifier,
									  self.room_capacity,
									  room_name)
		return identifier

	# Remove rooms that are empty
	def remove_empty(self):
		for roomId in list(self.rooms.keys()):
			if self.rooms[roomId].is_empty():
				del self.rooms[roomId]

	# Send a message to a all the players in the room
	def send(self, identifier, roomId, message, sock):
		if roomId not in self.rooms:
			print('Room not found')

		room = self.rooms[roomId]
		if not room.is_in_room(identifier):
			print('Not in room')

		for player in room.players:
			if player.identifier != identifier:
				player.send_udp(identifier, message)

	# Send a message only to one player in a room
	def sendto(self, identifier, roomId, recipients, message, sock):
		if roomId not in self.rooms:
			print('Room not found')

		room = self.rooms[roomId]
		if not room.is_in_room(identifier):
			print('Not in room')
   
		if isinstance(recipients, str):
			recipients = [recipients]
			
		for player in room.players:
			if player.identifier in recipients:
				player.send_udp(identifier, message)
