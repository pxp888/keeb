import asyncio
import zmq.asyncio
import configparser
import win32api
import win32con
from keymap import win32map, extended_keys
from asyncio import WindowsSelectorEventLoopPolicy

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

config = configparser.ConfigParser()


def setConfig(paths):
	global config
	for path in paths:
		if os.path.exists(path):
			cfi = config.read(path)
			print('Config file : ', path)
			print(cfi)
			print(config['DEFAULT']['serverip'])
			return
		else:
			continue


async def recvthings(qin):
	context = zmq.asyncio.Context()
	socket = context.socket(zmq.SUB)
	socket.connect(config['DEFAULT']['serverIP'])
	socket.setsockopt(zmq.SUBSCRIBE, config['DEFAULT']['clientID'].encode('utf-8'))
	while True:
		topic = await socket.recv_string()
		data = await socket.recv_pyobj()
		if data[0] < 23: 
			# print(topic, data)
			await qin.put(data)


async def pushKeys(qin):
	mouseDown = {272:win32con.MOUSEEVENTF_LEFTDOWN, 273:win32con.MOUSEEVENTF_RIGHTDOWN, 274:win32con.MOUSEEVENTF_MIDDLEDOWN}
	mouseUp = {272:win32con.MOUSEEVENTF_LEFTUP, 273:win32con.MOUSEEVENTF_RIGHTUP, 274:win32con.MOUSEEVENTF_MIDDLEUP}

	while True:
		etype, value, code = await qin.get()
		if etype == 1:
			if code in mouseDown:
				if value == 1:
					win32api.mouse_event(mouseDown[code], 0, 0, 0, 0)
				elif value == 0:
					win32api.mouse_event(mouseUp[code], 0, 0, 0, 0)
				continue

			if code in extended_keys:
				down = 0|win32con.KEYEVENTF_EXTENDEDKEY
				up = win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP
				c = extended_keys[code]
			else:
				down = 0 
				up = win32con.KEYEVENTF_KEYUP
				try:
					c = win32map[code]
				except KeyError:
					print('Key not found:', code)
					continue

			if value == 1:
				win32api.keybd_event(c, 0, down, 0)
			elif value == 0:
				win32api.keybd_event(c, 0, up, 0)
			elif value == 2:
				win32api.keybd_event(c, 0, up, 0)
				win32api.keybd_event(c, 0, down, 0)
		elif etype == 2:
			if code == 0:
				win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(value), 0, 0, 0)
			elif code == 1:
				win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(value), 0, 0)
			elif code == 8:
				win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120*value, 0)


async def main():
	qin = asyncio.Queue()
	await asyncio.gather(recvthings(qin), pushKeys(qin))


if __name__ == '__main__':
	paths = ['C:\\Users\\pxper\\Documents\\Config.ini','C:\\Users\\pxper\\Documents\\code\\keeb\\Config.ini']
	setConfig(paths)
	asyncio.run(main())

