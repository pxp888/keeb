import multiprocessing as mp
import evdev
from evdev import UInput, ecodes as e
import zmq
import time


userInput = UInput()

# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepAlive
# 4 change target (sender only)
# 5 quit

def sendthings(qoo):
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:64023")

	target = 'x'
	while True:
		mtype, data = qoo.get()
		if mtype == 4:
			target = data
			continue
		socket.send_string(target, zmq.SNDMORE)
		socket.send_pyobj((mtype, data))


def getKeys(keyboard, qoo):
	local = False
	try:
		with keyboard.grab_context():
			for event in keyboard.read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					if event.value==0:
						if event.code > 183:
							if event.code < 188:
								if event.code==184:
									qoo.put((4,'x'))
									local = False
								if event.code==185:
									qoo.put((4,'y'))
									local = False
								if event.code==186:
									local = True
								if event.code==187:
									qoo.put((5,0))
									break
								continue
					if local:
						localtype(event.value, event.code)
					else:
						qoo.put((event.value, event.code))
	except KeyboardInterrupt:
		print('interrupted!')
		pass


def localtype(a, b):
	if a == 1:
		userInput.write(e.EV_KEY, b, 1)
	elif a == 0:
		userInput.write(e.EV_KEY, b, 0)
	elif a == 2:
		userInput.write(e.EV_KEY, b, 0)
		userInput.write(e.EV_KEY, b, 1)
	userInput.syn()
	# print('local', a, b)


def keepAlive(qoo):
	while True:
		qoo.put((3,0))
		time.sleep(.01)


if __name__ == '__main__':
	qoo = mp.Queue()
	st = mp.Process(target=sendthings,args=(qoo,))
	st.start()

	ka = mp.Process(target=keepAlive,args=(qoo,))
	ka.start()
	
	time.sleep(1)

	# cat /proc/bus/input/devices | less
	# devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
	
	keyboard = evdev.InputDevice('/dev/input/event8')


	getKeys(keyboard, qoo)

	time.sleep(1)
	st.terminate()
	ka.terminate()

