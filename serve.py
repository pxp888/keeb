import multiprocessing as mp
import evdev
from evdev import UInput, AbsInfo, ecodes as e
import zmq
import time

userInput = UInput()
history = ''


# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepAlive
# 4 change target
# 5 quit

def getKeyboard(names):
	# if names is not a list, make it a list
	if not isinstance(names, list):
		names = [names]
	devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
	for device in devices:
		if device.name in names:
			print(device.name)
			print(device.phys)
			print(device.info)
			print('------------------')
			return device
	return None 


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


def record(a,b):
	global history
	if a < 2:
		n = str(a)+str(b)+'-'
		history += n
		history = history[-20:]
		print(history)


def getKeys(qoo, deviceNames):
	# keyboard = evdev.InputDevice('/dev/input/event0')
	keyboard = getKeyboard(deviceNames)
	if keyboard is None:
		print('no keyboard found!')
		return
	
	local = False
	try:
		with keyboard.grab_context():
			for event in keyboard.read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					# record(event.value, event.code)
					if event.code > 183 and event.code < 188:
						if event.value==0:
							if event.code==184:
								local = False
								qoo.put((4,'x'))
							if event.code==185:
								local = False
								qoo.put((4,'y'))
							if event.code==186:
								local = True
							if event.code==187:
								qoo.put((5,0))
								break
						continue
					if local:
						localType(event.value, event.code)
					else:
						qoo.put((event.value, event.code))
	except KeyboardInterrupt:
		print('interrupted!')
		pass


def localType(a, b):
	if a == 1:
		userInput.write(e.EV_KEY, b, 1)
	elif a == 0:
		userInput.write(e.EV_KEY, b, 0)
	elif a == 2:
		userInput.write(e.EV_KEY, b, 0)
		userInput.write(e.EV_KEY, b, 1)
	userInput.syn()


def keepAlive(qoo):
	while True:
		try:
			qoo.put((3,0),1)
		except:
			pass
		time.sleep(.01)


if __name__ == '__main__':
	qoo = mp.Queue(maxsize=200)
	
	st = mp.Process(target=sendthings,args=(qoo,))
	st.start()

	ka = mp.Process(target=keepAlive,args=(qoo,))
	ka.start()

	time.sleep(1)

	deviceNames = ['Keebio Keebio Iris Rev. 4','OLKB Planck Light']
	mediaNames = ['Keebio Keebio Iris Rev. 4 Consumer Control','OLKB Planck Light Consumer Control']
	
	gm = mp.Process(target=getKeys,args=(qoo,mediaNames))
	gm.start()

	getKeys(qoo, deviceNames)
	
	time.sleep(1)

	st.terminate()
	ka.terminate()
	gm.terminate()

