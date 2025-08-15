import whisper
import pyaudio
import numpy as np
import torch
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

_model = None
def get_model() -> bool:
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔍 Kullanılacak cihaz: {device}")
        _model = whisper.load_model("large", device=device)
        print("✅ Whisper modeli belleğe yüklendi.")
        return True
    return False

def transcribe_from_mic():
    global _model
    if _model is None:
        return
    language = "tr"
    record_seconds = 5

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print(f"🎤 {record_seconds} saniye boyunca konuşun...")
    frames = [stream.read(CHUNK, exception_on_overflow=False) for _ in range(int(RATE / CHUNK * record_seconds))]

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_np = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
    print("Ses analiz ediliyor...")
    result = _model.transcribe(audio_np, language=language)
    return result['text'].strip()