import asyncio
import zmq.asyncio
import configparser
import win32api
import win32con
from keymap import win32map, extended_keys
from asyncio import WindowsSelectorEventLoopPolicy

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

config = configparser.ConfigParser()
config.read(['C:\\Users\\pxper\\Documents\\Config.ini'])


# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepalive


async def recvthings(qin):
	context = zmq.asyncio.Context()
	socket = context.socket(zmq.SUB)
	socket.connect(config['DEFAULT']['serverIP'])
	socket.setsockopt(zmq.SUBSCRIBE, config['DEFAULT']['clientID'].encode('utf-8'))
	while True:
		topic = await socket.recv_string()
		data = await socket.recv_pyobj()
		if data[0] < 3: 
			# print(topic, data)
			await qin.put(data)


async def pushKeys(qin):
	while True:
		mtype, b = await qin.get()
		if b in extended_keys:
			down = 0|win32con.KEYEVENTF_EXTENDEDKEY
			up = win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP
			c = extended_keys[b]
		else:
			down = 0 
			up = win32con.KEYEVENTF_KEYUP
			try:
				c = win32map[b]
			except KeyError:
				print('Key not found:', b)
				continue

		if mtype==1:
			win32api.keybd_event(c, 0, down, 0)
		elif mtype==0:
			win32api.keybd_event(c, 0, up, 0)
		elif mtype==2:
			win32api.keybd_event(c, 0, up, 0)
			win32api.keybd_event(c, 0, down, 0)

async def main():
	qin = asyncio.Queue()
	await asyncio.gather(recvthings(qin), pushKeys(qin))


if __name__ == '__main__':
	asyncio.run(main())

