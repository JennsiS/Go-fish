'''
Universidad del Valle de Guatemala
Redes - CC3067
Proyecto 2

Integrantes:
- Luis Quezada 18028
- Jennifer Sandoval 18962
- Esteban del Valle 18221
'''

import random
import json

class Game():

	countPlayers = 0
	deck = []
	ocean = []
	turn = 1
	hands = []
	points = []

	def __init__(self,countPlayers):
		self.countPlayers = countPlayers
		self.createDeck()
		self.ramdomizeFirstTurn()
		self.getPlayerCards()
		self.createOcean()

	def createDeck(self):
		# Last digit indicates the suit of the card (DHSC)
		self.deck = [
		"AD","2D","3D","4D","5D","6D","7D","8D","9D","10D","JD","QD","KD",
		"AH","2H","3H","4H","5H","6H","7H","8H","9H","10H","JH","QH","KH",
		"AS","2S","3S","4S","5S","6S","7S","8S","9S","10S","JS","QS","KS",
		"AC","2C","3C","4C","5C","6C","7C","8C","9C","10C","JC","QC","KC",
		]

	def resetDeck(self):
		self.createDeck()

	def ramdomizeFirstTurn(self):
		self.turn = random.randint(1,self.countPlayers)

	def getCard(self):
		randomCardIndex = random.randint(0, len(self.deck)-1)
		return self.deck.pop(randomCardIndex)

	def getPlayerCards(self):
		playerCards = []
		handRange = 7

		if self.countPlayers > 2:
			handRange = 5

		for i in range(self.countPlayers):
			hand = []
			self.points.append(0)
			for i in range(handRange):
				hand.append(self.getCard())
			playerCards.append(hand)
		self.hands = playerCards
		return playerCards

	# Llamar despues de repartir las cartas
	def createOcean(self):
		ocean = []
		for i in range(len(self.deck)):
			ocean.append(self.getCard())
		self.ocean = ocean
		return ocean

	# Llamar despues de la jugada
	def updateTurn(self):
		if (self.turn >= self.countPlayers):
			self.turn = 1
		else:
			self.turn += 1

		# skip if hand empty
		if len(self.hands[self.turn-1]) == 0:
			self.turn += 1

	# Selecting a card from the ocean
	def fishing(self,pos):
		pos -= 1 # corretion cuz user uses 1 to n
		if pos < len(self.ocean) and pos >=0:
			card = self.ocean.pop(pos)
			self.hands[self.turn-1].append(card)
			return True
		else:
			return False

	def askCard(self,a,b,value):

		if len(self.hands[b-1]) == 0:
			return False

		handB = self.hands[b-1]

		toGive = []
		toKeep = []
		for card in handB:
			if value != card[0:-1]:
				toKeep.append(card)
			else:
				toGive.append(card)
		self.hands[b-1] = toKeep

		if len(toGive) == 0:
			return False
		else:
			self.hands[a-1] += toGive
			return True

	# Llamar cada jugada antes de update turn
	def checkEmptyHands(self):
		for hand in self.hands:
			if len(hand) == 0 and len(self.ocean) != 0:
				# If ocean has 5 or more draws 5, else draws left over cards
				if len(self.ocean) >= 5:
					toDraw = 5
				else:
					toDraw = len(self.ocean)

				for i in range(toDraw):
					hand.append(self.ocean.pop(1))

	def getHand(self):
		return self.hands[self.turn-1]

	# Llamar despues de cada askCard
	def checkFOK(self):
		player = self.turn
		hand = self.hands[player-1]
		groups = []
		fok = []
		for i in hand:
			groups.append(i[0:-1])
		my_dict = {i:groups.count(i) for i in groups}
		toKeep = []

		for key in my_dict.keys():
			if my_dict[key] == 4:
				fok = key
				
				print('>> Player',player,'has obtained a group!')
				self.points[player-1] += 1

				for card in hand:
					if card[0:-1] != fok:
						toKeep.append(card)

		if len(toKeep) > 0:
			self.hands[player-1] = toKeep

	# Llamar cada turn
	def checkWin(self):
		if (len(self.ocean)==0):
			counter = 0
			# Verificando si las manos de los jugadores se encuentran vacias
			for hand in self.hands:
				if len(hand) == 0:
					counter += 1
			if (counter == self.countPlayers):
				# Verificar los puntos de los usuarios
				maxPoints = max(self.points)
				winners = []
				for k in range(len(self.points)):
					if (self.points[k] == maxPoints):
						winners.append(k+1)
				if (len(winners)>1):
					print(">> It's a tie, players: ", winners)
				else:
					print(">> Player",winners[0],"has won!!!")

				print(">> Final points:")
				cont = 1
				for p in self.points:
					print("\t-",cont," Points:",p)
				return True
			else:
				#continuar con el juego
				return False
		else:
			#continuar con el juego
			return False

	def adoptGameState(self,countPlayers,hands,ocean,turn,points):
		self.countPlayers = countPlayers
		self.hands = hands
		self.ocean = ocean
		self.turn = turn
		self.points = points

	def stateToString(self):
		print("\tPlayers:",self.countPlayers,"\n\tTurn:",self.turn)
		print("\tHands:")
		cont = 1
		for hand in self.hands:
			print("\t  -",cont,":",hand)
			cont += 1
		print("\tOcean:",self.ocean)

		print("\tPoints:")
		cont = 1
		for p in self.points:
			print("\t  -",cont," Points:",p)
			cont += 1

	# Make Game JSON Serializable
	def toJSON(self):
		return json.dumps({"countPlayers":self.countPlayers,"hands":self.hands,"ocean":self.ocean,"turn":self.turn,"points":self.points})

