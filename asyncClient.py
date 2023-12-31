from evdev import UInput, ecodes as e
import asyncio
import zmq.asyncio
import configparser
import os 
import logging 


logging.basicConfig(filename='/home/pxp/Documents/asyncClient.log', level=logging.DEBUG, format='%(levelname)s - %(asctime)s  >  %(message)s')


"""Global Variables"""
config = configparser.ConfigParser()

userInput = UInput({e.EV_KEY: [i for i in range(246)[1:]] })
mouseInput = UInput({
	e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA], 
	e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_HWHEEL], })
msv = {272: 90001, 273: 90002, 274: 90003, 275: 90004, 276: 90005}


def setConfig(paths):
	global config
	for path in paths:
		if os.path.exists(path):
			cfi = config.read(path)
			logging.log(logging.INFO, 'Config file : ' + path)
			logging.log(logging.INFO, cfi)
			logging.log(logging.INFO, config['DEFAULT']['serverip'])
			return 0
		else:
			continue
	logging.log(logging.ERROR, 'No config file found')
	return 1


async def recvthings(qin):
	context = zmq.asyncio.Context()
	socket = context.socket(zmq.SUB)
	socket.connect(config['DEFAULT']['ServerIP'])
	socket.setsockopt(zmq.SUBSCRIBE, config['DEFAULT']['clientID'].encode('utf-8'))
	while True:
		topic = await socket.recv_string()
		data = await socket.recv_pyobj()
		if data[0] != 23:
			await qin.put(data)


async def doStuff(qin):
	while True:
		etype, value, code = await qin.get()
		if etype == e.EV_KEY:
			if code >= 272 and code <= 276:
				mouseInput.write(e.EV_MSC, 4, msv[code])
				mouseInput.write(etype, code, value)
				mouseInput.syn()
				continue
			userInput.write(etype, code, value)
			userInput.syn()
		elif etype == e.EV_REL:
			value = value * 2
			mouseInput.write(etype, code, value)
			mouseInput.syn()
		elif etype == 23:
			continue


async def main():
	paths = ['/home/pxp/Documents/keeb.ini','/home/pxp/Documents/code/keeb/Config.ini','/home/pxp/keeb/Config.ini']
	setConfig(paths)

	qin = asyncio.Queue()
	await asyncio.gather(recvthings(qin), doStuff(qin))


if __name__ == '__main__':
	asyncio.run(main())

