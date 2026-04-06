import evdev
from evdev import UInput, ecodes as e
import asyncio
import configparser
import os
import sys
import termios

# Globals
config = configparser.ConfigParser()
mouseInput = UInput({
	e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, e.KEY_VOLUMEDOWN, e.KEY_VOLUMEUP], 
	e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_HWHEEL, 11, 12], 
	e.EV_MSC: [4] # MSC_SCAN
})

mouseKeyValues = {272: 90001, 273: 90002, 274: 90003, 275: 90004, 276: 90005}
vScroll = 0.0  
hScroll = 0.0  
sensitivity = 1.0


def setConfig(paths):
	global config
	for path in paths:
		if os.path.exists(path):
			config.read(path)
			print(f'Config file found: {path}')
			return 0
	print('No config file found.', file=sys.stderr)
	return 1


async def localtype(etype, value, code):
	if etype == e.EV_KEY:
		if code in mouseKeyValues:
			mouseInput.write(e.EV_MSC, 4, mouseKeyValues[code])
			mouseInput.write(etype, code, value)
			mouseInput.syn()
		elif code in (e.KEY_VOLUMEDOWN, e.KEY_VOLUMEUP):
			mouseInput.write(etype, code, value)
			mouseInput.syn()
	elif etype == e.EV_REL:
		mouseInput.write(etype, code, value)
		mouseInput.syn()


handler = localtype


async def scrollFunc(etype, value, code):
	"""translates mouse translation to mouse wheel events, for custom scroll wheel"""
	global vScroll
	global hScroll
	global sensitivity
	if code == 8: # REL_WHEEL
		if value > 0:
			await handler(e.EV_KEY, 1, e.KEY_VOLUMEUP)
			await handler(e.EV_KEY, 0, e.KEY_VOLUMEUP)
			return
		elif value < 0:
			await handler(e.EV_KEY, 1, e.KEY_VOLUMEDOWN)
			await handler(e.EV_KEY, 0, e.KEY_VOLUMEDOWN)
			return
	if code == 1: # REL_Y
		# High-resolution scroll (120 units = 1 notch)
		hiResValue = int(value * -12 * sensitivity) # multiplier 12 (120 * 0.1), inverted
		await handler(etype, hiResValue, 11)

		# Legacy fallback (standard ticks)
		vScroll += float(value * 0.1 * sensitivity)
		ticks = int(vScroll)
		vScroll -= float(ticks)
		if ticks != 0:
			await handler(etype, -ticks, e.REL_WHEEL)
		return
	if code == 0: # REL_X
		# Horizontal high-resolution scroll
		hiResValue = int(value * 9 * sensitivity) # multiplier 9 (120 * 0.075)
		await handler(etype, hiResValue, 12)

		# Legacy fallback
		hScroll += float(value * 0.075 * sensitivity)
		ticks = int(hScroll)
		hScroll -= float(ticks)
		if ticks != 0:
			await handler(etype, ticks, e.REL_HWHEEL)
		return


async def rapooScrollFunc(etype, value, code):
	"""translates mouse translation to mouse wheel events, only vertical, for RAPOO mouse"""
	global vScroll
	global sensitivity
	if code == 1: # REL_Y
		# High-resolution scroll (multiplier 1.2 = 120 * 0.01)
		hiResValue = int(value * 1.2 * sensitivity)
		await handler(etype, hiResValue, 11)

		# Legacy fallback
		vScroll += float(value * 0.01 * sensitivity)
		ticks = int(vScroll)
		vScroll -= float(ticks)
		if ticks != 0:
			await handler(etype, ticks, e.REL_WHEEL)
	return

mousehandler = handler

async def getKeys(device, fixed_mousehandler=None):
	"""Gets key events from the mouse and handles them"""
	global handler
	global mousehandler
	
	specialCodes = {}
	try:
		toggle_code = int(config['server'].get('ScrollToggleCode', '276'))
	except Exception:
		toggle_code = 276
	specialCodes[toggle_code] = ('scrollToggle', 0) # e.BTN_EXTRA

	with device.grab_context():
		while True:
			async for event in device.async_read_loop():
				if event.type == e.EV_KEY:
					if event.code in specialCodes:
						if event.value == 1: continue
						com = specialCodes[event.code]
						if com[0] == 'scrollToggle' and fixed_mousehandler is None:
							if mousehandler == scrollFunc:
								mousehandler = handler
							else:
								mousehandler = scrollFunc
					else:
						await handler(event.type, event.value, event.code)
				elif event.type == e.EV_REL:
					mh = fixed_mousehandler if fixed_mousehandler else mousehandler
					await mh(event.type, event.value, event.code)


async def mousemain():
	fd = None
	old_termios = None
	try:
		if sys.stdin.isatty():
			fd = sys.stdin.fileno()
			old_termios = termios.tcgetattr(fd)
			new_termios = termios.tcgetattr(fd)
			new_termios[3] = new_termios[3] & ~termios.ECHO
			termios.tcsetattr(fd, termios.TCSADRAIN, new_termios)
	except Exception:
		pass

	try:
		# Set up config
		paths = ['./scrollmode.ini']
		setConfig(paths)

		await asyncio.sleep(1) # make sure keys are not pressed when devices are captured

		# Set up devices
		tasks = []
		try:
			targetDevices = config['server']['DeviceNames'].split('|')
		except KeyError:
			print("Config error: ['server']['DeviceNames'] missing.", file=sys.stderr)
			return

		global sensitivity
		try:
			sensitivity = float(config['server'].get('Sensitivity', '100')) / 100.0
		except Exception:
			sensitivity = 1.0

		devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
		for device in devices:
			# print('checking device:', device.name)
			for t in targetDevices:
				if t and t in device.name:
					print('Capturing : ', device.name)
					if 'RAPOO' in device.name:
						task = asyncio.create_task(getKeys(device, fixed_mousehandler=rapooScrollFunc))
					else:
						task = asyncio.create_task(getKeys(device))
					tasks.append(task)

		if not tasks:
			print("No devices matched the configuration.")
			return

		await asyncio.gather(*tasks)
	finally:
		if fd is not None and old_termios is not None:
			try:
				termios.tcsetattr(fd, termios.TCSADRAIN, old_termios)
			except Exception:
				pass



if __name__ == '__main__':
	try:
		asyncio.run(mousemain())
	except KeyboardInterrupt:
		pass
