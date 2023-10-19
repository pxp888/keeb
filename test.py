import multiprocessing as mp
import evdev
from evdev import UInput, ecodes as e
import zmq
import time
import socket
import pickle
import platform 
import socket


def usendthings(qoo):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('192.168.1.29', 64023)
	while True:
		target, data = qoo.get()
		message = target.encode() + b':' + pickle.dumps(data)
		sock.sendto(message, server_address)


def sendthings(qoo):
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:64023")
	while True:
		# data = qoo.get()
		target, data = qoo.get()
		# socket.send_string('k', zmq.SNDMORE)
		socket.send_string(target, zmq.SNDMORE)
		socket.send_pyobj(data)


def getKeys(keyboard, qoo):
	ui = UInput()
	target='k'
	try:
		with keyboard.grab_context():
			for event in keyboard.read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					print(event.value, event.code)
					if event.code > 183 and event.code < 188:
						if event.code==184: target='k'
						if event.code==185: target='local'
						if event.code==186: target='d'
						if event.code==187: 
							qoo.put((target, (event.value, event.code)))
							break
						continue
					if target=='local':
						localtype(ui, event.value, event.code)
						continue
					qoo.put((target, (event.value, event.code)))
	except KeyboardInterrupt:
		print('interrupted!')
		pass


def localtype(ui, a, b):
	if a == 1:
		ui.write(e.EV_KEY, b, 1)
	elif a == 0:
		ui.write(e.EV_KEY, b, 0)
	elif a == 2:
		ui.write(e.EV_KEY, b, 0)
		ui.write(e.EV_KEY, b, 1)
	ui.syn()  # Sync the device to send the events


def keepalive(qoo):
	while True:
		qoo.put(('0', (0, 0)))
		time.sleep(.01)


if __name__ == '__main__':
	qoo = mp.Queue()
	# st = mp.Process(target=sendthings,args=(qoo,))
	st = mp.Process(target=usendthings,args=(qoo,))
	st.start()

	ka = mp.Process(target=keepalive,args=(qoo,))
	ka.start()
	
	time.sleep(1)

	# cat /proc/bus/input/devices | less
	# devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
	if platform.processor()=='x86_64':
		keyboard = evdev.InputDevice('/dev/input/event8')
	else:
		keyboard = evdev.InputDevice('/dev/input/event2')
	if keyboard is None: 
		print('no keyboard found')
		exit()

	getKeys(keyboard, qoo)

	time.sleep(1)
	st.terminate()
	ka.terminate()


