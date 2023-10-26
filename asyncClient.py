from evdev import UInput, ecodes as e
import asyncio
import zmq.asyncio
import configparser
import os 


"""message types """
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepalive


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
        if data[0] < 3: 
        	await qin.put(data)


async def pushKeys(qin):
	userInput = UInput()
	while True:
		mtype, b = await qin.get()
		userInput.write(e.EV_KEY, b, mtype)
		userInput.syn()


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
    await asyncio.gather(recvthings(qin), pushKeys(qin))


if __name__ == '__main__':
    asyncio.run(main())

