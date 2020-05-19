import socket
import pickle
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from multiprocessing import Queue, Process
import time

def receive(q, s):
    msg= 1
    s.settimeout(5)

    data = b''
    arrcount = 0

    try: 
        while msg: # and arrcount<75:
            arrcount += 1
            msg = s.recvfrom(4385)[0]
            x = pickle.loads(msg)
            print(x.shape)
            # print(arrcount)
            # arr.append(x)
            q.put(x)

    except socket.timeout:
        print("timed out")
        return 0

    print("DONE")

def play_voice(q, fs):
    # if q.qsize() > 35:
    arr = []
    print("starting queuedebunk")
    while not q.empty():
        arr.append(q.get())
    print("finished: ", len(arr))
    new_arr = arr[0]
    for index in range(1, len(arr)):
        new_arr = np.concatenate((new_arr, arr[index]))

    arr.clear()
    print(new_arr.shape)
    sd.play(new_arr, fs)
    sd.wait()
    write('output.wav', fs, new_arr)


if __name__ == "__main__":
    fs = 20000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("192.168.2.108", 8080))
    sock.settimeout(5)

    queue = Queue()
    # information_array = []

    # first_reception = Process(target=receive, args=(queue, sock))
    # first_reception.start()
    
    recv_proc = Process(target=receive, args=(queue, sock))
    recv_proc.start()
    # time.sleep(1)
    # while queue.empty() or queue.qsize() > 35:
    #     print("waiting")
    time.sleep(6)
    while not queue.empty():
        print("playing voice")
        play_proc = Process(target=play_voice, args=(queue, fs))
        play_proc.start()
        play_proc.join()

    recv_proc.join()
    # first_reception.join()
    sock.close()

