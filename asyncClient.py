from evdev import UInput, ecodes as e
import asyncio
import zmq.asyncio
import configparser

config = configparser.ConfigParser()
config.read(['/home/pxp/Documents/code/keeb/Config.ini','/home/pxp/keeb/Config.ini'])


# mtype, data
# 0 keyup
# 1 keydown
# 2 keyhold
# 3 keepalive
# 4 change target (sender only)
# 5 quit


async def recvthings(qin):
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(config['DEFAULT']['ServerIP'])
    # socket.connect("tcp://localhost:64024")
    socket.setsockopt(zmq.SUBSCRIBE, b'x')

    while True:
        topic = await socket.recv_string()
        data = await socket.recv_pyobj()
        if data[0]!=3: 
        	await qin.put(data)


async def pushKeys(qin):
	userInput = UInput()
	while True:
		mtype, b = await qin.get()
		if mtype==5: return 
		if mtype==1:
			userInput.write(e.EV_KEY, b, 1)
		elif mtype==0:
			userInput.write(e.EV_KEY, b, 0)
		elif mtype==2:
			userInput.write(e.EV_KEY, b, 2)
		userInput.syn()


async def main():
    qin = asyncio.Queue()

    task1 = asyncio.create_task(recvthings(qin))
    task2 = asyncio.create_task(pushKeys(qin))
    await asyncio.gather(task1, task2)


if __name__ == '__main__':
    asyncio.run(main())

