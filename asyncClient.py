from evdev import UInput, ecodes as e
import asyncio
import zmq.asyncio
import configparser
import os 


"""Global Variables"""
config = configparser.ConfigParser()


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
	userInput = UInput()
	mouseInput = UInput({
		e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA], 
		e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL], })
	msv = {272: 90001, 273: 90002, 274: 90003, 275: 90004, 276: 90005}

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
			mouseInput.write(etype, code, value)
			mouseInput.syn()
		elif etype == 23:
			continue


async def main():
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


	qin = asyncio.Queue()
	await asyncio.gather(recvthings(qin), doStuff(qin))


if __name__ == '__main__':
	asyncio.run(main())

