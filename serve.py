import multiprocessing as mp
import evdev
from evdev import UInput, AbsInfo, ecodes as e
import zmq
import time
import select
import configparser

config = configparser.ConfigParser()
config.read(['/home/pxp/Documents/code/keeb/Config.ini','/home/pxp/keeb/Config.ini'])

userInput = UInput()

# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepAlive
# 4 change target
# 5 quit


def getKeyboard(names):
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


def getKeys(qoo, deviceNames):
	keyboard = getKeyboard(deviceNames)
	if keyboard is None:
		print('no keyboard found!')
		return

	local = False
	with keyboard.grab_context():
		while True:
			r, w, x = select.select([keyboard], [], [])
			event = keyboard.read_one()
			if event.type == evdev.ecodes.EV_KEY:
				if event.code > 183 and event.code < 188:
					if event.value == 0:
						if event.code == 184:
							local = False
							qoo.put((4, 'x'))
						if event.code == 185:
							local = False
							qoo.put((4, 'y'))
						if event.code == 186:
							local = True
						if event.code == 187:
							qoo.put((5, 0))
							break
					continue
				if local:
					localType(event.value, event.code)
				else:
					qoo.put((event.value, event.code))


def localType(a, b):
	if a == 1:
		userInput.write(e.EV_KEY, b, 1)
	elif a == 0:
		userInput.write(e.EV_KEY, b, 0)
	elif a == 2:
		userInput.write(e.EV_KEY, b, 2)
	userInput.syn()


def keepAlive(qoo):
	while True:
		qoo.put((3, 0))
		time.sleep(.01)


if __name__ == '__main__':
	qoo = mp.Queue(maxsize=100)

	st = mp.Process(target=sendthings, args=(qoo,))
	ka = mp.Process(target=keepAlive, args=(qoo,))
	st.start()
	ka.start()

	time.sleep(1)

	deviceNames = config['server']['DeviceNames'].split('|')
	mediaNames = config['server']['MediaNames'].split('|')

	gm = mp.Process(target=getKeys, args=(qoo, mediaNames))
	gm.start()

	getKeys(qoo, deviceNames)
	time.sleep(1)

	st.terminate()
	ka.terminate()
	gm.terminate()
