import sounddevice as sd
import numpy as np

def callback(indata, frames, time, status):
    volume = np.linalg.norm(indata) * 10
    print(f"Volume: {volume:.2f}")

print("Speak into the microphone... Press Ctrl+C to stop.")

with sd.InputStream(callback=callback):
    while True:
        pass