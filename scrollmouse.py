import multiprocessing as mp
import evdev
from evdev import UInput, AbsInfo, ecodes as e
import asyncio
import zmq.asyncio
import configparser
import os

from asyncServer import *


async def mousemain():
	# Set up config
	paths = ['/home/pxp/Documents/mouse.ini','/home/pxp/Documents/code/keeb/mouse.ini','/home/pxp/keeb/mouse.ini']
	for path in paths:
		if os.path.exists(path):
			cfi = config.read(path)
			print('Config file : ', path)
			print(cfi)
			print(config['DEFAULT']['serverip'])
			break
		else:
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

	global target
	global handler
	target = 'local'
	handler = localtype

	await asyncio.gather(*tasks)
	# await asyncio.gather(*tasks, sendthings(qoo), keepAlive(qoo))


if __name__ == '__main__':
	asyncio.run(mousemain())

