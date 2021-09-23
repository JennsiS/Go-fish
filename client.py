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
import time
import sys
import random
from game import Game
from utils import  showCards,isNumber

class Client:

	def __init__(self,server_host,server_port_tcp=1234,server_port_udp=1234,client_port_udp=1235, username='player'):
		self.identifier = None
		self.server_message = []
		self.room_id = None
		self.client_udp = ("0.0.0.0", client_port_udp)
		self.lock = threading.Lock()
		self.server_listener = SocketThread(self.client_udp,self,self.lock)
		self.server_listener.start()
		self.server_udp = (server_host, server_port_udp)
		self.server_tcp = (server_host, server_port_tcp)
		self.username = username
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

	def getGame(self):
		message = json.dumps({"action": "get_game", "payload": self.room_id, "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		gameData = self.parseData(data)
		return gameData

	def setGame(self, game):
		message = json.dumps({"action": "set_game", "payload": self.room_id, "identifier": self.identifier, "game": game.toJSON()})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		message = self.parseData(data)

	def getClientGameId(self):
		message = json.dumps({"action": "get_client_game_id", "payload": self.room_id, "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		client_game_id = self.parseData(data)
		return client_game_id

	def isRoomReady(self):
		message = json.dumps({"action": "room_ready", "payload": self.room_id, "identifier": self.identifier})
		self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_tcp.connect(self.server_tcp)
		self.sock_tcp.send(message.encode())
		data = self.sock_tcp.recv(1024)
		self.sock_tcp.close()
		is_ready = self.parseData(data)
		return is_ready

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

	def getRoom(self):
		rooms = self.getRooms()
		for room in rooms:
			if room['id'] == self.room_id:
				return room

	def send(self, message):
		message = json.dumps({"action": "send","payload": {"message": message},"room_id": self.room_id,"identifier": self.identifier})
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(message.encode(), self.server_udp)

	def sendTo(self, recipients, message):
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

	def disconnect(self):
		self.server_listener.stop()


class SocketThread(threading.Thread):
	def __init__(self, addr, client, lock):
		threading.Thread.__init__(self)
		self.client = client
		self.lock = lock
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(addr)

	def run(self):
		while True:
			try:
				data, addr = self.sock.recvfrom(1024)
				self.lock.acquire()
				self.client.server_message.append(data)
			except:
				pass
			finally:
				self.lock.release()

	def stop(self):
		self.sock.close()



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Simple game server')
	parser.add_argument('--tcpport',dest='tcp_port',help='Listening tcp port',default="1234")
	parser.add_argument('--udpport',dest='udp_port',help='Listening udp port',default="1234")

	args = parser.parse_args()

	# Setup id and client port
	client_port = 2000 + random.randint(1,1000)

	# Game Intro
	print("\n\n====================================================")
	print("\t   ____         _____ _     _     ")
	print("\t  / ___| ___   |  ___(_)___| |__  ")
	print("\t | |  _ / _ \\  | |_  | / __| '_ \\ ")
	print("\t | |_| | (_) | |  _| | \\__ \\ | | |")
	print("\t  \\____|\\___/  |_|   |_|___/_| |_|")
	print("====================================================\n")

	print("\t  a python implementation by JEL\n\n")

	insConf = input(">> Would you like to read Go Fish Instructions? [y/n]: ")

	if insConf.lower() == 'y':
		# Instructions
		print('\n|| ===================================================================== ||')
		print('\t\t\t    HOW TO PLAY\n')
		print('Go fish is played with a French deck and can be played by 2+ players.')
		x = input("\t\t  == PRESS ENTER TO CONTINUE ==")
		print('\n>> Object of the Game: The goal is to win the most "books" of cards. A book is any four of a kind, such as four kings, four aces, and so on.')
		x = input("\t\t  == PRESS ENTER TO CONTINUE ==")
		print('\n>> Hands: If there are 2 players, 7 cards are dealt to each. If there are 3 or more, 5 cards are dealt to each.')
		x = input("\t\t  == PRESS ENTER TO CONTINUE ==")
		print('\n>> Ocean: The cards that are not dealt to the players are placed in the middle of the board face down, this set is called the ocean')
		x = input("\t\t  == PRESS ENTER TO CONTINUE ==")
		print('\n>> The beggining: The game starts by selecting one of the players at random to start then the turns will be followed in the order in which the players entered the room.')
		x = input("\t\t  == PRESS ENTER TO CONTINUE ==")
		print('\n>> In your turn: You can ask any other player in the room if they have any cards with a certain number (You can only ask for cards with a number that are in your hand). If the player you asked has one or more cards of that number, he must give them all to you and your turn continues. Otherwise, the player you asked tells you "Go fish" and you must take a card from the ocean choosing the position of the card you want and it is the next player´s turn.')
		x = input("\t\t  == PRESS ENTER TO CONTINUE ==")
		print('\n>> Points: You get points every time you collect a group of 4 cards with the same number. These cards are removed from your hand and from the game. ')
		x = input("\t\t  == PRESS ENTER TO CONTINUE ==")
		print('\n<!> If a player runs out of cards, they must take back the initial amount from the ocean if there are still available. If there are no more cards to take, the player has no more turns and must wait for the game to end.')
		x = input("\t\t  == PRESS ENTER TO CONTINUE ==")
		print('\n>> The End: The game ends when neither player has any cards in their hand and there are no more cards in the ocean. The player who has accumulated the most groups of 4 cards (the player with the maximum number of points) wins.')
		print('\n|| ===================================================================== ||')

	#  Register on server
	username = input("\n>> Enter your username to use in the game: ")
	client = Client("127.0.0.1",int(args.tcp_port),int(args.udp_port),client_port,username)
	

	try:
		# Join client to available room
		client.autojoin()
		print("\n>> Connected to room ",client.room_id)
		print(">> [ roomstate",client.room_id,"]")
		print(">> [ room",client.room_id,"]\n\n")
	except Exception as e:
		print("<!> Could not autojoin,",e)

	# Wait for room to fill
	room = client.getRoom()
	connectedPlayers,maxPlayers = room["connected_players"],room["capacity"]

	while connectedPlayers < maxPlayers:
		print("\n>> Waiting for other players to start game... (",connectedPlayers,"/",maxPlayers,")\n",sep="")
		time.sleep(3)
		room = client.getRoom()
		connectedPlayers,maxPlayers = room["connected_players"],room["capacity"]

	print("\n>> Waiting for other players to start game... (",connectedPlayers,"/",maxPlayers,")\n",sep="")

	client_id = client.getClientGameId()

	# Defensive prog player list
	player_id_list = []
	for i in range(connectedPlayers):
		player_id_list.append(str(i+1))

	player_id_list.remove(str(client_id))

	# Init game
	game = Game(connectedPlayers)

	#  Main GAME loop
	print("\n>> Game starting!!!\n\n")
	continueLoop = True

	while continueLoop:
		msg = client.getMessages()
		if len(msg) != 0:
			for message in msg:
				message = json.loads(message)
				sender, value = message.popitem()
				print("[",value["name"],"]: ",value["message"],sep="")

		gameData = client.getGame()
		gameData = json.loads(gameData)
		game.adoptGameState(gameData['countPlayers'],gameData['hands'],gameData['ocean'],gameData['turn'],gameData['points'])

		if game.checkWin() == False:
			if game.turn == client_id:
				print("\n>> Your turn!")
				cmd = input("[chat/play/exit]: ")

				while cmd not in ["chat","play","exit"]:
					cmd = input("[chat/play/exit]: ")

				if cmd == "chat":
					msgtext = input(">> Chat msg: ")
					client.send({"name": username,"message": msgtext})

				elif cmd == "play":
					hand = game.getHand()
					print(">> Your current hand:")
					showCards(hand)

					to_id = input(">> Ask player "+str(player_id_list)+": ")
					while to_id not in player_id_list:
						print("<!> Bad input.\n")
						to_id = input(">> Ask player "+str(player_id_list)+": ")
					validValues = game.getValidCardNumbers()
					card_number = input(">> Card values to choose from "+ str(validValues)+": ")
					card_number = card_number.upper()
					while card_number not in validValues:
						print("<!> Bad input.\n")
						card_number = input(">> Card values to choose from "+ str(validValues)+": ")
						card_number = card_number.upper()
					if game.askCard(client_id,int(to_id),card_number) == False:
						# Player asked does not have any cards to give, go fish!
						print("\n>> Go fish!")
						if len(game.ocean) > 0:
							print(">> Pick an ocean card...")
							cardPos = isNumber(">> Ocean card position [1 to "+str(len(game.ocean))+"]: ")
							while ((int(cardPos) not in range(1,len(game.ocean)+1))):
								print("<!> Bad input.\n")
								cardPos = isNumber(">> Ocean card position [1 to "+str(len(game.ocean))+"]: ")
							cardPos =int(cardPos)
							game.fishing(cardPos)
						else:
							print(">> Ocean empty, no fishing for you!")
						game.checkEmptyHands()
						
						foksFound = game.checkFOK()
						if foksFound == 1:
							print(">> You made",foksFound,"group.")
							msgtext = "made "+foksFound+" group!"
							client.send({"name": username,"message": msgtext})
						elif foksFound > 1:
							print(">> You made",foksFound,"groups.")
							msgtext = "made "+foksFound+" groups!"
							client.send({"name": username,"message": msgtext})

						hand = game.getHand()
						print(">> Your current hand:")
						showCards(hand)

						game.updateTurn()
						print("\n>> Player ",game.turn,"'s' turn!\n",sep="")
						print("\t ||------ Chat ------||")
					else:
						# Player asked gave cards, turn does not change
						print("\n>> Card(s) given! Your turn continues...")
						game.checkEmptyHands()

						foksFound = game.checkFOK()
						if foksFound == 1:
							print(">> You made",foksFound,"group.")
							msgtext = "made "+foksFound+" group!"
							client.send({"name": username,"message": msgtext})
						elif foksFound > 1:
							print(">> You made",foksFound,"groups.")
							msgtext = "made "+foksFound+" groups!"
							client.send({"name": username,"message": msgtext})

						hand = game.getHand()
						print(">> Your current hand:")
						showCards(hand)

					client.setGame(game)

				
				elif cmd == "exit":
					game.updateTurn()
					client.setGame(game)
					client.leaveRoom()
					print(">> Left room... disconnecting.")
					client.disconnect()
					sys.exit()
			else:
				#foo = input("\t\t- PRESS ENTER to refresh -\n")
				time.sleep(2)
		else:
			print("\n>> Thanks for playing!\n")
			client.leaveRoom()
			client.disconnect()
			sys.exit()

