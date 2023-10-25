import multiprocessing as mp
import evdev
from evdev import UInput, AbsInfo, ecodes as e
import asyncio
import zmq.asyncio
import configparser


# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepalive
# 4 change target (sender only)



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
	socket.bind("tcp://*:64023")

	target = 'x'
	while True:
		mtype, data = await qoo.get()
		if mtype == 4:
			target = data
			continue
		if target=='z':
			if mtype > 2: continue
			userInput.write(e.EV_KEY, data, mtype)
			userInput.syn()
			continue
		await socket.send_string(target, zmq.SNDMORE)
		await socket.send_pyobj((mtype, data))


async def keepAlive(qoo):
	while True:
		await qoo.put((3, 0))
		await asyncio.sleep(.01)


async def getKeys(qoo, deviceNames):
	keyboard = getKeyboard(deviceNames)
	if keyboard is None:
		print('no keyboard found!')
		return
	
	special = {}
	special[184] = (4, 'x')
	special[185] = (4, 'y')
	special[186] = (4, 'z')

	with keyboard.grab_context():
		while True:
			async for event in keyboard.async_read_loop():
				if event.type == evdev.ecodes.EV_KEY:
					if event.code in special:
						if event.value == 0:
							await qoo.put(special[event.code])
						continue
					await qoo.put((event.value, event.code))


async def main():
	await asyncio.sleep(1)
	qoo = asyncio.Queue()
	deviceNames = config['server']['DeviceNames'].split('|')
	mediaNames = config['server']['MediaNames'].split('|')
	await asyncio.gather(sendthings(qoo), getKeys(qoo, deviceNames), keepAlive(qoo), getKeys(qoo, mediaNames))


if __name__ == '__main__':
	asyncio.run(main())

