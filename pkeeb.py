import pynput.keyboard
import multiprocessing as mp
import threading
import zmq

def recvthings(qin):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:64023")
    socket.setsockopt(zmq.SUBSCRIBE, b'k')

    while True:
        topic = socket.recv_string()
        data = socket.recv_pyobj()
        # qin.put((topic,data))
        print(topic,data)

def sendthings(qoo):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:64023")
    while True:
        data = qoo.get()
        socket.send_string('k', zmq.SNDMORE)
        socket.send_pyobj(data)

def on_press(key):
    qoo.put(('d', key))
    return True

def on_release(key):
    qoo.put(('u', key))
    return True

if __name__ == '__main__':
    qin = mp.Queue()
    qoo = mp.Queue()

    rt = mp.Process(target=recvthings,args=(qin,))
    rt.start()
    # st = mp.Process(target=sendthings,args=(qoo,))
    # st.start()
    st = threading.Thread(target=sendthings,args=(qoo,))
    st.start()

    with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()