from pynput.keyboard import Key, Controller, KeyCode

import multiprocessing as mp
import zmq

def recvthings(qin):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:64023")
    socket.setsockopt(zmq.SUBSCRIBE, b'k')

    while True:
        topic = socket.recv_string()
        data = socket.recv_pyobj()
        qin.put(data)
        # print(topic,data)

    
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
        if type(b)==KeyCode:
            print('KeyCode', b)
            k = b 
        elif type(b)==Key:
            print('Key', b)
            k = b.value 
        
        print(k)
        if a==1:
            keyboard.press(k)
        else:
            keyboard.release(k)
