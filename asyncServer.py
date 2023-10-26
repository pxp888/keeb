import multiprocessing as mp
import evdev
from evdev import UInput, AbsInfo, ecodes as e
import asyncio
import zmq.asyncio
import configparser
import os 


"""message types"""
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepalive


"""Global Variables"""
config = configparser.ConfigParser()
userInput = UInput()
target = 'x'


async def sendthings(qoo):
	"""Sends events to the clients"""
	context = zmq.asyncio.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:64023")

	global target 
	while True:
		mtype, data = await qoo.get()
		await socket.send_string(target, zmq.SNDMORE)
		await socket.send_pyobj((mtype, data))


async def keepAlive(qoo):
	"""keep the clients responsive"""
	while True:
		await qoo.put((3, 0))
		await asyncio.sleep(.01)


async def sendItem(value, code, qoo):
	await qoo.put((value, code))


async def localtype(value, code, qoo):
	userInput.write(e.EV_KEY, code, value)
	userInput.syn()


async def getKeys(qoo, device):
	"""Gets key events from the keyboard and puts them in qoo"""
	
	global target 
	targetCodes = {}
	targetCodes[184] = 'x'
	targetCodes[185] = 'y'
	targetCodes[186] = 'z'
	handler = sendItem

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
					await handler(event.value, event.code, qoo)


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

