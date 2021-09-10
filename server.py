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
import sys
import socket
import select
import pickle


def userAccepted(username):
	dprotocol = {
		'type': 'useraccepted',
		'username': username,
	}

	msg = pickle.dumps(dprotocol)
	msg = bytes(f"{len(msg):<{headerLen}}", "utf-8") + msg
	return msg

def sendAll(username,message):
	dprotocol = {
		'type': 'message',
		'username': username,
		'message': message
	}

	msg = pickle.dumps(dprotocol)
	msg = bytes(f"{len(msg):<{headerLen}}", "utf-8") + msg
	return msg

def receiveMessage(clientSocket):
	try:
		msgHeader = clientSocket.recv(headerLen)
		if not len(msgHeader):
			return False
		data = pickle.loads(clientSocket.recv(int(msgHeader.decode('utf-8').strip())))
		return {"header": msgHeader, "data": data}
	except:
		return False


# Args
parser = argparse.ArgumentParser()
parser.add_argument('-p','--port',help='Server port to connect.')
args = parser.parse_args()

# Constantes
headerLen = 10 
ip = "127.0.0.1"
clients = {}

try:
	port = int(args.port)
except:
	print("\n<!> Bad port, run 'python server.py -h' por more info.\n")
	sys.exit()

# Sockets y coneccion
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((ip,port))
serverSocket.listen()
socketsList = [serverSocket]

print("\n\n>> Server set IP["+str(ip)+"] PORT["+str(port)+"]\n")


while True:
	readSockets, _, exceptionSockets = select.select(socketsList, [], socketsList)

	for notifiedSocket in readSockets:

		if notifiedSocket == serverSocket:
			clientSocket, clientAddress = serverSocket.accept()
			user = receiveMessage(clientSocket)

			if user is False:
				continue
			if user['data']['type'] == 'signin':
				msg = userAccepted(user['data']['username'])
				clientSocket.send(msg)
				signinok = False

				while not signinok:
					message = receiveMessage(clientSocket)
					if message is False:
						continue
					if message['data']['type'] == "signinok":
						signinok = True

				socketsList.append(clientSocket)
				clients[clientSocket] = user
				print(">> "+user['data']['username']+" connected.")

		else:
			message = receiveMessage(notifiedSocket)

			if message is False:
				print(">> ["+clients[notifiedSocket]['data']['username']+"] closed connection.")
				socketsList.remove(notifiedSocket)
				del clients[notifiedSocket]
				continue
			user = clients[notifiedSocket]
			
			if message['data']['type'] == 'sendmessage':
				print(">> [",user['data']['username'],"]: ",message['data']['message'],sep="")
				msg = sendAll(user['data']['username'],message['data']['message'])
				for clientSocket in clients:
					if clientSocket != notifiedSocket:
						clientSocket.send(msg)
			else:
				print(">> [",message['data']['username'],"]: ",message['data']['type'])

		for notifiedSocket in exceptionSockets:
			socketsList.remove(notifiedSocket)
			del clients[notifiedSocket]

