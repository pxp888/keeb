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
vScroll = 0.0  # for mouse wheel
hScroll = 0.0  # for mouse wheel


async def sendthings(qoo):
	"""Sends events to the clients"""
	global target
	context = zmq.asyncio.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:64023")
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


async def scrollFunc(etype, value, code, qoo):
	"""translates mouse translation to mouse wheel events, for custom scroll wheel"""
	global vScroll
	global hScroll
	if code==8:
		if value > 0:
			await sendItem(e.EV_KEY, 1, 115, qoo)
			await sendItem(e.EV_KEY, 0, 115, qoo)
			return
		elif value < 0:
			await sendItem(e.EV_KEY, 1, 114, qoo)
			await sendItem(e.EV_KEY, 0, 114, qoo)
			return
	if code == 1:
		code = e.REL_WHEEL
		vScroll += float(value*0.1)
		value = int(vScroll)
		vScroll -= float(value)
		value = value * -1
		await sendItem(etype, value, code, qoo)
		return
	if code == 0:
		code = e.REL_HWHEEL
		hScroll += float(value*0.075)
		value = int(hScroll)
		hScroll -= float(value)
		# value = value * -1
		await sendItem(etype, value, code, qoo)
		return


handler = sendItem  # or localtype, for keyboard events
mousehandler = scrollFunc  # or sendItem, for mouse events


async def getKeys(qoo, device):
	"""Gets key events from the keyboard and puts them in qoo"""
	global target
	global handler
	global mousehandler
	
	specialCodes = {}
	specialCodes[184] = ('target','x')
	specialCodes[185] = ('target','y')
	specialCodes[186] = ('target','local')
	specialCodes[276] = ('scrollToggle',0)

	with device.grab_context():
		while True:
			async for event in device.async_read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					if event.code in specialCodes:
						if event.value == 1: continue
						com = specialCodes[event.code]
						if com[0] == 'target':
							target = com[1]
							if target == 'local':
								handler = localtype
							else:
								handler = sendItem
						if com[0] == 'scrollToggle':
							if mousehandler == scrollFunc:
								mousehandler = sendItem
							else:
								mousehandler = scrollFunc
					else:
						await handler(event.type, event.value, event.code, qoo)
				elif event.type == evdev.ecodes.EV_REL:
					await mousehandler(event.type, event.value, event.code, qoo)


async def main():
	# Set up config
	paths = ['/home/pxp/Documents/keeb.ini','/home/pxp/Documents/code/keeb/Config.ini','/home/pxp/Config.ini','/home/pxp/keeb/Config.ini']
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

