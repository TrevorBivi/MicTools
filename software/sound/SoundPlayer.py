from threading import Thread

class SoundPlayer(object):
    def __init__(self, devices, sr=48000, chunk_size = 1024)
        self.devices = devices
        self.sr = sr
        self.chunk_size = chunk_size
        self.sounds = []
        self.streams = {}

    def add_sound(sound):
        for d in sound.devices:
            if d not in self.streams:
                self.add_stream(d)

    def remove_sound(sound):
        self.sounds.remove(sound)
        
    def add_stream(device):
        stream = OutputStream(samplerate=self.sr, device=device, channels=1, blocksize=self.chunk_size, dtype='float32').__enter__())
        self.streams[device] = stream

    def remove_stream(device):
        self.streams[device].__exit__()
        del self.streams[device]

    def play_sounds():
        def play_thread():
            while True:
                for s in sounds:
                    chunk = s.next_chunk()
                    for d in s.devices:
                        self.streams[d].write(chunk)
                
        thread = Thread(target=play_thread)
        thread.daemon = True
        thread.start()
