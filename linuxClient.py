import multiprocessing as mp
import zmq
import evdev
from evdev import UInput, AbsInfo, ecodes as e


# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepalive
# 4 change target (sender only)
# 5 quit
# 6 toggle scroll
# 7 mouse x
# 8 mouse y 
# 9 mouse click
# 10 mouse scroll


def recvthings(qin, qoo):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://192.168.1.29:64023")
	socket.setsockopt(zmq.SUBSCRIBE, b'x')
	while True:
		topic = socket.recv_string()
		data = socket.recv_pyobj()
		qin.put(data)


def pushKeys(qin):
	userInput = UInput()
	print(userInput)
	while True:
		mtype, b = qin.get()
		if mtype==5: return 
		if mtype==1:
			userInput.write(e.EV_KEY, b, 1)
		elif mtype==0:
			userInput.write(e.EV_KEY, b, 0)
		elif mtype==2:
			userInput.write(e.EV_KEY, b, 0)
			userInput.write(e.EV_KEY, b, 1)
		userInput.syn()


if __name__ == '__main__':
	qin = mp.Queue()
	qoo = mp.Queue()

	rt = mp.Process(target=recvthings,args=(qin, qoo))
	rt.start()

	pushKeys(qin)

	rt.terminate()

