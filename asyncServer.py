import multiprocessing as mp
import evdev
from evdev import UInput, AbsInfo, ecodes as e
import asyncio
import zmq.asyncio
import configparser
import os 

# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepalive


config = configparser.ConfigParser()
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

userInput = UInput()
target = 'x'

def getKeyboard(names):
	"""Returns the first keyboard found with a name in names"""
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


async def getKeys(qoo, deviceNames):
	"""Gets key events from the keyboard and puts them in qoo"""
	keyboard = getKeyboard(deviceNames)
	if keyboard is None:
		print('no keyboard found!')
		return
	
	global target 
	targetCodes = {}
	targetCodes[184] = 'x'
	targetCodes[185] = 'y'
	targetCodes[186] = 'z'
	handler = sendItem


	with keyboard.grab_context():
		while True:
			async for event in keyboard.async_read_loop():
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
	await asyncio.sleep(1)
	qoo = asyncio.Queue()
	deviceNames = config['server']['DeviceNames'].split('|')
	mediaNames = config['server']['MediaNames'].split('|')
	await asyncio.gather(sendthings(qoo), getKeys(qoo, deviceNames), keepAlive(qoo), getKeys(qoo, mediaNames))


if __name__ == '__main__':
	asyncio.run(main())

