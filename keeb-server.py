import pynput.keyboard
from pynput.keyboard import Key, Controller, KeyCode
import multiprocessing as mp
import zmq

def recvthings(qin):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://localhost:64023")
	socket.setsockopt(zmq.SUBSCRIBE, b'k')

	while True:
		topic = socket.recv_string()
		data = socket.recv_pyobj()
		# qin.put((topic,data))
		print(data)

def sendthings(qoo):
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:64023")
	while True:
		data = qoo.get()
		socket.send_string('k', zmq.SNDMORE)
		socket.send_pyobj(data)




def on_press(key):
	if key==Key.esc:
		return False
	qoo.put((1, key))

def on_release(key):
	qoo.put((0, key))
	pass
	
if __name__ == '__main__':
	qin = mp.Queue()
	qoo = mp.Queue()

	# rt = mp.Process(target=recvthings,args=(qin,))
	# rt.start()
	st = mp.Process(target=sendthings,args=(qoo,))
	st.start()

	with pynput.keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True) as listener:
		listener.join()
	print('all done')

