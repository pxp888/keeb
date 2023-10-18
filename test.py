import multiprocessing as mp
import evdev
from evdev import UInput, ecodes as e
import keyboard as kblib
import zmq
import time



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

	# cat /proc/bus/input/devices | less

	# devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
	# keyboard = None
	# for device in devices:
	# 	print(device.name)


def getKeys(keyboard, qoo):
	ui = UInput()
	target='k'
	try:
		with keyboard.grab_context():
			for event in keyboard.read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					print(event.value, event.code)
					if event.code>183:
						if event.code<188:
							if event.code==187: break
							if event.code==184: target='k'
							if event.code==185: target='local'
							if event.code==186: target='d'
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


if __name__ == '__main__':
	qoo = mp.Queue()
	st = mp.Process(target=sendthings,args=(qoo,))
	# st = mp.Process(target=localtype,args=(qoo,))
	st.start()

	time.sleep(1)

	keyboard = evdev.InputDevice('/dev/input/event8')
	if keyboard is None: exit()

	getKeys(keyboard, qoo)

	time.sleep(1)
	st.terminate()

# thoeunththoeunhoteuh

