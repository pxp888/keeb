import multiprocessing as mp
import zmq
import pyautogui

from keymap import key_map

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
	socket.connect("tcp://192.168.1.36:64023")
	socket.setsockopt(zmq.SUBSCRIBE, b'x')
	while True:
		topic = socket.recv_string()
		data = socket.recv_pyobj()
		qin.put(data)


def pushKeys(qin):
	while True:
		mtype, b = qin.get()
		if mtype==5: return 
		if b in key_map:
			b = key_map[b]
		else:
			print('unmapped')
			continue 
		if mtype==1:
			pyautogui.keyDown(b)
		elif mtype==0:
			pyautogui.keyUp(b)
		elif mtype==2:
			pyautogui.keyUp(b)
			pyautogui.keyDown(b)


if __name__ == '__main__':
	qin = mp.Queue()
	rt = mp.Process(target=recvthings,args=(qin,))
	rt.start()
	pushKeys(qin)

	rt.terminate()
	