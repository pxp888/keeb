import asyncio
import zmq.asyncio
import configparser

config = configparser.ConfigParser()
config.read(['/home/pxp/Documents/code/keeb/Config.ini','/home/pxp/keeb/Config.ini'])

async def recvthings(qin):
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(config['DEFAULT']['ServerIP'])
    socket.setsockopt(zmq.SUBSCRIBE, b'x')

    while True:
        topic = await socket.recv_string()
        data = await socket.recv_pyobj()
        if data[0]!=3: 
        	await qin.put(data)

async def print_data(qin):
    while True:
        data = await qin.get()
        print(data)

async def main():
    qin = asyncio.Queue()

    task1 = asyncio.create_task(recvthings(qin))
    task2 = asyncio.create_task(print_data(qin))

    await task1
    await task2

if __name__ == '__main__':
    asyncio.run(main())