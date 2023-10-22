import multiprocessing as mp
import zmq
from evdev import UInput, ecodes as e


# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepalive
# 4 change target (sender only)
# 5 quit


def recvthings(qin, qoo):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://10.0.0.11:64023")
	socket.setsockopt(zmq.SUBSCRIBE, b'x')
	while True:
		topic = socket.recv_string()
		data = socket.recv_pyobj()
		qin.put(data)


def pushKeys(qin):
	userInput = UInput()
	while True:
		mtype, b = qin.get()
		if mtype==5: return 
		if mtype==1:
			userInput.write(e.EV_KEY, b, 1)
		elif mtype==0:
			userInput.write(e.EV_KEY, b, 0)
		elif mtype==2:
			userInput.write(e.EV_KEY, b, 2)
		userInput.syn()


def moveMouse(qoo):
	userInput = UInput({
		e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE],
		e.EV_REL: [e.REL_X, e.REL_Y],
		})


if __name__ == '__main__':
	qin = mp.Queue()
	qoo = mp.Queue()

	rt = mp.Process(target=recvthings,args=(qin, qoo))
	rt.start()

	pushKeys(qin)

	rt.terminate()

