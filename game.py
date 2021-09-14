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


class game():

	countPlayers = 0
	deck = []
	ocean = []

	def __init__(self,countPlayers):
		self.countPlayers = countPlayers
		self.createDeck()


	def createDeck(self):
		# Last digit indicates the suit of the card (DHSC)
		self.deck = [
		"AD","2D","3D","4D","5D","6D","7D","8D","9D","10D","JD","QD","KD",
		"AH","2H","3H","4H","5H","6H","7H","8H","9H","10H","JH","QH","KH",
		"AS","2S","3S","4S","5S","6S","7S","8S","9S","10S","JS","QS","KS",
		"AC","2C","3C","4C","5C","6C","7C","8C","9C","10C","JC","QC","KC",
		]

	def resetDeck(self):
		self.createDeck

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
			for i in range(handRange):
				hand.append(self.getCard())
			playerCards.append(hand)
		return playerCards

	def createOcean(self):
		for i in range(len(self.deck)):
			self.ocean.append(self.getCard())

	def turns(self):
		pass

	def fishing(self,xPos,yPos):
		#Selecting a card from the ocean
		pass



g = game(4)
print(g.getPlayerCards())
print(g.deck)
g.createOcean()
print(g.ocean)





