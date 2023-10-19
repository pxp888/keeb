import multiprocessing as mp
import zmq
import keyboard
import socket
import pickle


# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepalive
# 4 change target (sender only)
# 5 quit


def recvthings(qin):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://192.168.1.33:64023")
	socket.setsockopt(zmq.SUBSCRIBE, b'x')

	while True:
		topic = socket.recv_string()
		data = socket.recv_pyobj()
		qin.put(data)


def netKeys(qin):
	while True:
		mtype, b = qin.get()
		if mtype==5: return 
		# if b==187: return
		# try:
		# print(a,b)
		if mtype==1:
			keyboard.press(b)
		elif mtype==0:
			keyboard.release(b)
		elif mtype==2:
			keyboard.release(b)
			keyboard.press(b)
		
		# except:
		# 	print('error')
		# 	pass

if __name__ == '__main__':
	qin = mp.Queue()
	rt = mp.Process(target=recvthings,args=(qin,))
	# rt = mp.Process(target=urecvthings,args=(qin,))
	rt.start()

	netKeys(qin)

	rt.terminate()
