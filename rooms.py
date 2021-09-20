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

	def isFull(self):
		if len(self.players) == self.capacity:
			return True
		else:
			return False

	def join(self, player):
		if not self.is_full():
			self.players.append(player)
		else:
			pass
