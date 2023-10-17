import multiprocessing as mp 
# from evdev import InputDevice, categorize, ecodes, UInput
import evdev
import zmq
import select 


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

def getKeys():
	dev = evdev.InputDevice('/dev/input/event8') # replace X with the event number of your keyboard
	dev.grab()
	for event in dev.read_loop():
		if event.type == evdev.ecodes.EV_KEY:
			key_event = event.code
			kcode = evdev.ecodes.KEY[key_event]
			if kcode=='KEY_ESC':
				dev.ungrab()
				return
			qoo.put((event.value, event.code))
			print(event.value, kcode)

def normKeys():
	dev = evdev.InputDevice('/dev/input/event8') # replace X with the event number of your keyboard
	for event in dev.read_loop():
		if event.type == evdev.ecodes.EV_KEY:
			key_event = event.code
			kcode = evdev.ecodes.KEY[key_event]
			if kcode=='KEY_ESC':
				return
			print('n', kcode)
			qoo.put((event.value, event.code))

if __name__ == '__main__':
	qin = mp.Queue()
	qoo = mp.Queue()

	# rt = mp.Process(target=recvthings,args=(qin,))
	# rt.start()
	st = mp.Process(target=sendthings,args=(qoo,))
	st.start()

	# while 1:
	getKeys()
	# normKeys()

	st.terminate()
