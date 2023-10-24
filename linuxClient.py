import multiprocessing as mp
import zmq
from evdev import UInput, ecodes as e
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


def recvthings(qin):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect(config['DEFAULT']['ServerIP'])
	socket.setsockopt(zmq.SUBSCRIBE, b'x')
	while True:
		topic = socket.recv_string()
		data = socket.recv_pyobj()
		qin.put(data)


def pushKeys(qin):
	userInput = UInput()
	while True:
		mtype, b = qin.get()
		if mtype==5: return 
		if mtype==1:
			userInput.write(e.EV_KEY, b, 1)
		elif mtype==0:
			userInput.write(e.EV_KEY, b, 0)
		elif mtype==2:
			userInput.write(e.EV_KEY, b, 2)
		userInput.syn()


if __name__ == '__main__':
	qin = mp.Queue()
	qoo = mp.Queue()

	rt = mp.Process(target=recvthings,args=(qin, ))
	rt.start()

	pushKeys(qin)

	rt.terminate()

