import multiprocessing as mp
import zmq
import keyboard
import time


def recvthings(qin):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://192.168.1.29:64023")
	socket.setsockopt(zmq.SUBSCRIBE, b'k')

	while True:
		topic = socket.recv_string()
		data = socket.recv_pyobj()
		qin.put(data)

def netKeys(qin):
	while True:
		a, b = qin.get()
		if b==187: return
		# try:
		print(a,b)
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
	rt = mp.Process(target=recvthings,args=(qin,))
	rt.start()

	netKeys(qin)

	rt.terminate()
