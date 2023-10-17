import pynput 
from pynput.keyboard import Key, Controller, KeyCode
import multiprocessing as mp
import zmq


def recvthings(qin):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://192.168.1.29:64023")
    socket.setsockopt(zmq.SUBSCRIBE, b'k')

    while True:
        topic = socket.recv_string()
        data = socket.recv_pyobj()
        qin.put(data)
        # print(topic,data)

def evdev_key_value_to_pynput_keycode(evdev_key_value):
    try:
        k = pynput.keyboard.KeyCode(evdev_key_value)
        # k = KeyCode.from_vk(evdev_key_value)
        print(k, type(k))
        return k
    except ValueError:
        return None

if __name__ == '__main__':
    qin = mp.Queue()
    qoo = mp.Queue()

    rt = mp.Process(target=recvthings,args=(qin,))
    rt.start()
    # st = mp.Process(target=sendthings,args=(qoo,))
    # st.start()
    
    keyboard = Controller()

    while 1:
        a,b = qin.get()
        # k = evdev_key_value_to_pynput_keycode(b)
        # print(k, type(k))
        print(a,b)

        # if a==1:
        #     keyboard.press(k)
        # else:
        #     keyboard.release(k)
