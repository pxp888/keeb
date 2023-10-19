import multiprocessing as mp
import zmq
import keyboard
import socket
import pickle


def recvthings(qin):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://192.168.1.33:64023")
	socket.setsockopt(zmq.SUBSCRIBE, b'k')

	while True:
		topic = socket.recv_string()
		data = socket.recv_pyobj()
		if topic=='k':
			qin.put(data)


def urecvthings(qin):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('0.0.0.0', 64023))
	while True:
		data, address = sock.recvfrom(1024)
		target, value = data.split(b':')
		value = pickle.loads(value)
		if target==b'a':
			qin.put(value)


def netKeys(qin):
	while True:
		a, b = qin.get()
		if b==187: return
		# try:
		# print(a,b)
		if a==1:
			keyboard.press(b)
		elif a==0:
			keyboard.release(b)
		elif a==2:
			keyboard.release(b)
			keyboard.press(b)
		
		# except:
		# 	print('error')
		# 	pass

if __name__ == '__main__':
	qin = mp.Queue()
	# rt = mp.Process(target=recvthings,args=(qin,))
	rt = mp.Process(target=urecvthings,args=(qin,))
	rt.start()

	netKeys(qin)

	rt.terminate()
