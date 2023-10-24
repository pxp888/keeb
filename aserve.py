import multiprocessing as mp
import evdev
from evdev import UInput, AbsInfo, ecodes as e
import time
import select
import asyncio
import zmq.asyncio
import configparser

config = configparser.ConfigParser()
config.read(['/home/pxp/Documents/code/keeb/Config.ini','/home/pxp/keeb/Config.ini'])

userInput = UInput()


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


async def sendthings(qoo):
	context = zmq.asyncio.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:64024")

	target = 'x'
	while True:
		mtype, data = await qoo.get()
		if mtype == 4:
			target = data
			continue
		await socket.send_string(target, zmq.SNDMORE)
		await socket.send_pyobj((mtype, data))


async def getKeys(qoo, deviceNames):
	keyboard = getKeyboard(deviceNames)
	if keyboard is None:
		print('no keyboard found!')
		return

	local = False
	with keyboard.grab_context():
		while True:
			async for event in keyboard.async_read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					if event.code > 183 and event.code < 188:
						if event.value == 0:
							if event.code == 184:
								local = False
								await qoo.put((4, 'x'))
							if event.code == 185:
								local = False
								await qoo.put((4, 'y'))
							if event.code == 186:
								local = True
							if event.code == 187:
								await qoo.put((5, 0))
								break
						continue
					if local:
						localType(event.value, event.code)
					else:
						await qoo.put((event.value, event.code))

def localType(value, code):
	if value == 1:
		userInput.write(e.EV_KEY, code, 1)
	elif value == 0:
		userInput.write(e.EV_KEY, code, 0)
	elif value == 2:
		userInput.write(e.EV_KEY, code, 2)
	userInput.syn()


async def main():
	qoo = asyncio.Queue()
	
	deviceNames = config['server']['DeviceNames'].split('|')
	task2 = asyncio.create_task(getKeys(qoo, deviceNames))
	task1 = asyncio.create_task(sendthings(qoo))
	await asyncio.gather(task2, task1)

if __name__ == '__main__':
	asyncio.run(main())



