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

def getBoard():
	devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
	keyboard = None
	for device in devices:
		print(device.name)
		if keyboard is None:
			if "keyboard" in device.name.lower():
				keyboard = device
				# break

	if keyboard is None:
		print("No keyboard found")
	else:
		print("Keyboard found: ", keyboard)
	return keyboard

def getKeys(keyboard, qoo):
	try:
		with keyboard.grab_context():
			for event in keyboard.read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					key_event = event.code
					kcode = evdev.ecodes.KEY[key_event]
					if kcode=='KEY_ESC':
						break
					print(event.value, kcode)
					qoo.put((event.value, event.code))
	except KeyboardInterrupt:
		pass


if __name__ == '__main__':
	qoo = mp.Queue()
	st = mp.Process(target=sendthings,args=(qoo,))
	st.start()
	time.sleep(1)
	
	# keyboard = getBoard()	
	keyboard = evdev.InputDevice('/dev/input/event8')

	if keyboard is None: exit()
	
	getKeys(keyboard, qoo)

	st.terminate()


