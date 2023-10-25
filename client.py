import threading 
import queue
import zmq
import win32api
import win32con


from keymap import win32map, extended_keys

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
	socket.connect("tcp://192.168.1.37:64023")
	socket.setsockopt(zmq.SUBSCRIBE, b'x')
	while True:
		topic = socket.recv_string()
		data = socket.recv_pyobj()
		if data[0]!=3:
			qin.put(data)


def pushKeys(qin):
	while True:
		mtype, b = qin.get()
		if mtype==5: return

		if b in extended_keys:
			down = 0|win32con.KEYEVENTF_EXTENDEDKEY
			up = win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP
			c = extended_keys[b]
		else:
			down = 0 
			up = win32con.KEYEVENTF_KEYUP
			try:
				c = win32map[b]
			except KeyError:
				print('Key not found:', b)
				continue

		if mtype==1:
			win32api.keybd_event(c, 0, down, 0)
		elif mtype==0:
			win32api.keybd_event(c, 0, up, 0)
		elif mtype==2:
			win32api.keybd_event(c, 0, up, 0)
			win32api.keybd_event(c, 0, down, 0)

if __name__ == '__main__':
	qin = queue.Queue()
	rt = threading.Thread(target=recvthings,args=(qin,))
	rt.start()
	pushKeys(qin)

	