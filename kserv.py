import multiprocessing as mp
import evdev
import zmq
import time

def sendthings(qoo):
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:64023")
	while True:
		data = qoo.get()
		socket.send_string('k', zmq.SNDMORE)
		socket.send_pyobj(data)

	# devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
	# keyboard = None
	# for device in devices:
	# 	print(device.name)

def getKeys(keyboard, qoo):
	try:
		with keyboard.grab_context():
			for event in keyboard.read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					print(event.value, event.code)
					qoo.put((event.value, event.code))
					if event.code==1: break
	except KeyboardInterrupt:
		print('interrupted!')
		pass

if __name__ == '__main__':
	qoo = mp.Queue()
	st = mp.Process(target=sendthings,args=(qoo,))
	st.start()

	time.sleep(1)

	keyboard = evdev.InputDevice('/dev/input/event8')
	if keyboard is None: exit()

	getKeys(keyboard, qoo)

	time.sleep(1)
	st.terminate()

