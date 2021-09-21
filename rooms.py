'''
Universidad del Valle de Guatemala
Redes - CC3067
Proyecto 2

Integrantes:
- Luis Quezada 18028
- Jennifer Sandoval 18962
- Esteban del Valle 18221
'''
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
	def isFull(self):
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
	def isEmpty(self):
		if len(self.players) == 0:
			return True
		else:
			return False

	# Checking if a specific player is inside the room
	def isInRoom(self, player_identifier):
		in_room = False
		for player in self.players:
			if player.identifier == player_identifier:
				in_room = True
				break
		return in_room
