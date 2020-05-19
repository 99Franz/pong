import sounddevice as sd
import pickle
from scipy.io.wavfile import write
import time
import socket
from multiprocessing import Process, Queue


def send_data(q, s):
    HOST = ("192.168.2.108", 8080)
    # print("sending")
    while not q.empty():
        print("sending")
        # s.sendall(q.get())
        s.sendto(q.get(), HOST)


def recordStream(q):
    print("start recording")
    duration = 10.0  # seconds
    fs = 20000
    sd.default.samplerate = fs

    try:
        def callback(indata, frames, time, status):
            # global allbytes
            if status:
                print(status)
            # allbytes += pickle.dumps(indata)
            # print(len(pickle.dumps(indata)))
            # sock.send(pickle.dumps(indata))
            data = pickle.dumps(indata)
            print("Länge: ", len(data))
            q.put(data)
            print(indata.shape)

        with sd.InputStream(channels=2, samplerate=fs, callback=callback):
            start = time.perf_counter()
            # while time.perf_counter()-start < duration:
            #     x = 1
            sd.sleep(int(duration * 1000))

        print("done wit it")
    except MemoryError:
        print("MemERROR")
        pass




if __name__ == "__main__":
    # print("Number of cpu : ", multiprocessing.cpu_count())
    # HOST = ("192.168.2.108", 8080)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.connect(HOST)
    sock.settimeout(10)

    queue = Queue()
    record_proc = Process(target=recordStream, args=(queue, ))

    print("starting record_proc")
    record_proc.start()

    print("stopping record_proc")
    time.sleep(1)
    print(queue)
    while not queue.empty():
        send_proc = Process(target=send_data, args=(queue, sock))
        print("starting send_proc")
        send_proc.start()
        send_proc.join()

    record_proc.join()


    sock.close()


    # output = pickle.loads(allbytes)
    # print(type(output))
    # print(output.shape)
    # sd.play(myrecording)
    # print(myrecording.shape)
    # sd.play(output)
    # write('output.wav', fs, myrecording)