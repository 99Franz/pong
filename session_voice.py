import sounddevice as sd
import pickle
from scipy.io.wavfile import write
import time
import socket
from multiprocessing import Process, Queue
import numpy as np
import keyboard


RECV_HOST = ("192.168.2.108", 8080)
SEND_HOST = ("192.168.2.108", 8080)


def send_data(q, s):
    # print("sending")
    while not q.empty():
        print("sending")
        # s.sendall(q.get())
        s.sendto(q.get(), SEND_HOST)


def record_stream(q):
    print("start recording")
    duration = 1.0  # seconds
    fs = 20000
    sd.default.samplerate = fs

    try:
        def callback(indata, frames, time, status):
            if status:
                print(status)
            data = pickle.dumps(indata)
            print("Länge: ", len(data))
            q.put(data)
            print(indata.shape)

        keyboard.wait("k")
        stream = sd.InputStream(channels=2, samplerate=fs, callback=callback)
        stream.start()
        # sd.sleep(int(duration * 1000))
        keyboard.wait("k")
        stream.stop()

        print("done wit it")
    except MemoryError:
        print("MemERROR")
        pass


def receive(q, s):
    msg = 1
    s.settimeout(100)

    data = b''
    arrcount = 0

    try:
        while msg:
            arrcount += 1
            msg = s.recvfrom(4385)[0]
            x = pickle.loads(msg)
            print("receiving")
            print(x.shape)
            q.put(x)

    except socket.timeout:
        print("timed out")
        return 0

    print("DONE")


def play_voice(q, fs):
    # if q.qsize() > 35:
    arr = []
    print("starting queue debunk")
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


def handle_sending():
    sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock_send.settimeout(10)
    start = time.perf_counter()

    while time.perf_counter() - start < 30:
        queue = Queue()
        record_proc = Process(target=record_stream, args=(queue,))

        print("starting record_proc")
        record_proc.start()

        while queue.empty():
            time.sleep(1)
            print("waiting")

        while not queue.empty():
            send_proc = Process(target=send_data, args=(queue, sock_send))
            print("starting send_proc")
            send_proc.start()
            send_proc.join()

        record_proc.join()
        print("stopping record_proc")
    sock_send.close()


def handle_receiving():
    fs = 20000
    # while time.perf_counter() - start < 30:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECV_HOST)
    sock.settimeout(20)

    queue = Queue()
    # information_array = []

    # first_reception = Process(target=receive, args=(queue, sock))
    # first_reception.start()

    recv_proc = Process(target=receive, args=(queue, sock))
    recv_proc.start()

    start = time.perf_counter()
    while time.perf_counter() - start < 30:
        while queue.empty():  # or queue.qsize() > 35:
            print("waiting")
            time.sleep(6)
        while not queue.empty():
            print("playing voice")
            play_proc = Process(target=play_voice, args=(queue, fs))
            play_proc.start()
            play_proc.join()

    recv_proc.join()
        # first_reception.join()
    sock.close()


if __name__ == "__main__":
    handle_send_proc = Process(target=handle_sending)
    handle_send_proc.start()
    handle_recv_proc = Process(target=handle_receiving)
    handle_recv_proc.start()

    keyboard.wait("esc")

    handle_send_proc.join()
    handle_recv_proc.join()







