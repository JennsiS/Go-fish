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
import errno
import pickle
import random
import zlib


def signIn(username):
	dprotocol = {
		'type': 'signin',
		'username': username
	}
	msg = pickle.dumps(dprotocol)
	msg = bytes(f"{len(msg):<{headerLen}}", "utf-8") + msg
	return msg

def correctSignIn():
	dprotocol = {
		"type":"signinok",
	}
	msg = pickle.dumps(dprotocol)
	msg = bytes(f"{len(msg):<{headerLen}}", "utf-8") + msg
	return msg

def sendMessage(message):
	crc32 = zlib.crc32(pickle.dumps(message))

	dprotocol = {
		"type":"sendmessage",
		"message": message
	}
	msg = pickle.dumps(dprotocol)
	msg = bytes(f"{len(msg):<{headerLen}}", "utf-8") + msg
	return msg

def receiveMessage(clientSocket,header=''):
	try:
		if header == '': 
			messageHeader = clientSocket.recv(headerLen)
		else:
			messageHeader = header
		if not len(messageHeader):
			return False
		
		messageLength  = int(messageHeader.decode('utf-8').strip())
		data = pickle.loads(clientSocket.recv(messageLength))
		msg = {"header": messageHeader, "data": data}
		return msg
	except:
		return False


# Args
parser = argparse.ArgumentParser()
parser.add_argument('-p','--port',help='Server port to connect.')
args = parser.parse_args()

# Constantes
headerLen = 10 
ip = "127.0.0.1"

try:
	port = int(args.port)
except:
	print("\n<!> Bad port, run 'python client.py -h' por more info.\n")
	sys.exit()

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((ip,port))
clientSocket.setblocking(False)
print("\n\n>> Connected to server IP["+str(ip)+"] PORT["+str(port)+"]\n")
signedIn = False

userN = input(">> Enter username: ")
msg = signIn(userN)
clientSocket.send(msg)

while not signedIn:
	try:
		while True:
			message = receiveMessage(clientSocket)
			if message:
				if message['data']['username'] == userN:
					print("\n\n>> Server set IP["+str(ip)+"] PORT["+str(port)+"]\n")
					print(">> Signed in as:",userN)
					msg = correctSignIn()
					clientSocket.send(msg)
					signedIn = True
					break
				else:
					print(">> Mismatch username:",message['data']['username'])
					print(">> Disconnecting.")
					sys.exit()

	except IOError as e:
		if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
			print('>> Error:',str(e))
			sys.exit()
		continue
	except Exception as e:
		print('>> Error:', str(e))
		sys.exit()

while True:

	print("\n\n\n GAME STATE \n\n\n")

	message = input("["+userN+"]: ")


	if message:
		msg = sendMessage(message)
		clientSocket.send(msg)

	try:
		while True:

			header = clientSocket.recv(headerLen)
			if not len(header):
				print(">> Server closed connection.")
				sys.exit()
			msg = receiveMessage(clientSocket,header)

			print("[",msg['data']['username'],"]: ",msg['data']['message'],sep="")

	except IOError as e:
		if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
			print('>> Error:',str(e))
			sys.exit()
		continue
	except Exception as e:
		print('>> Error:', str(e))
		sys.exit()

