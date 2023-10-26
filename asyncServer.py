import multiprocessing as mp
import evdev
from evdev import UInput, AbsInfo, ecodes as e
import asyncio
import zmq.asyncio
import configparser
import os



"""Global Variables"""
config = configparser.ConfigParser()
userInput = UInput()
mouseInput = UInput({
	e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA], 
	e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL], })
msv = {272: 90001, 273: 90002, 274: 90003, 275: 90004, 276: 90005}
target = 'x'


async def sendthings(qoo):
	"""Sends events to the clients"""
	context = zmq.asyncio.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:64023")

	global target
	while True:
		etype, value, code = await qoo.get()
		await socket.send_string(target, zmq.SNDMORE)
		await socket.send_pyobj((etype, value, code))


async def keepAlive(qoo):
	"""keep the clients responsive"""
	while True:
		await qoo.put((23, 0, 0))
		await asyncio.sleep(.01)


async def sendItem(etype, value, code, qoo):
	await qoo.put((etype, value, code))
	

async def localtype(etype, value, code, qoo):
	if etype == e.EV_KEY:
		if code >= 272 and code <= 276:
			mouseInput.write(e.EV_MSC, 4, msv[code])
			mouseInput.write(etype, code, value)
			mouseInput.syn()
			return
		userInput.write(etype, code, value)
		userInput.syn()
	elif etype == e.EV_REL:
		mouseInput.write(etype, code, value)
		mouseInput.syn()
	elif etype == 23:
		return 


handler = sendItem


async def getKeys(qoo, device):
	"""Gets key events from the keyboard and puts them in qoo"""

	global target
	global handler
	targetCodes = {}
	targetCodes[184] = 'x'
	targetCodes[185] = 'y'
	targetCodes[186] = 'z'
	

	with device.grab_context():
		while True:
			async for event in device.async_read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					if event.code in targetCodes:
						if event.value == 0:
							target = targetCodes[event.code]
							if target == 'z':
								handler = localtype
							else:
								handler = sendItem
						continue
					await handler(event.type, event.value, event.code, qoo)
				elif event.type == evdev.ecodes.EV_REL:
					await handler(event.type, event.value, event.code, qoo)


async def main():
	# Set up config
	paths = ['/home/pxp/Documents/keeb.ini','/home/pxp/Documents/code/keeb/Config.ini','/home/pxp/keeb/Config.ini']
	for path in paths:
		if os.path.exists(path):
			cfi = config.read(path)
			print(cfi)
			print(config['DEFAULT']['serverip'])
			break
		else:
			print("Config file not found at " + path)
			continue

	await asyncio.sleep(1) # make sure keys are not pressed when devices are captured
	qoo = asyncio.Queue()

	# Set up devices
	tasks = []
	targetDevices = config['server']['DeviceNames'].split('|')
	devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
	for device in devices:
		for t in targetDevices:
			if t in device.name:
				print('Capturing : ', device.name)
				task = asyncio.create_task(getKeys(qoo, device))
				tasks.append(task)

	await asyncio.gather(*tasks, sendthings(qoo), keepAlive(qoo))


if __name__ == '__main__':
	asyncio.run(main())

