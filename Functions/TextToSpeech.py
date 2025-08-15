#TextToSpeech.py


from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import os
import time
import threading

class AudioPlayer:
    def __init__(self, filepath):
        self.filepath = filepath
        self._stop_flag = threading.Event()
        self._play_thread = None

    def _play(self):
        try:
            with sf.SoundFile(self.filepath) as f:
                data = f.read(dtype='float32')
                samplerate = f.samplerate
                sd.play(data, samplerate)
                while sd.get_stream().active:
                    if self._stop_flag.is_set():
                        sd.stop()
                        break
                    time.sleep(0.1)
        except Exception as e:
            print(f"Oynatma hatası: {e}")

    def play(self):
        self._stop_flag.clear()
        self._play_thread = threading.Thread(target=self._play, daemon=True)
        self._play_thread.start()

    def stop(self):
        self._stop_flag.set()
        sd.stop()
        if self._play_thread:
            self._play_thread.join()
    
    def is_playing(self):
        try:
            return sd.get_stream().active
        except Exception:
            return False

player = None  # global player

def metni_olustur(metin):
    gecici_klasor = '..\\temps'
    if not os.path.exists(gecici_klasor):
        os.makedirs(gecici_klasor)
    cikti_dosyasi = os.path.join(gecici_klasor, 'okunan_metin.mp3')
    tts = gTTS(text=metin, lang='tr', slow=False)
    tts.save(cikti_dosyasi)
    return cikti_dosyasi

def metni_oku(metin):
    global player
    if player:
        player.stop()
        player = None

    dosya_yolu = metni_olustur(metin)
    player = AudioPlayer(dosya_yolu)
    player.play()

def tts_durdur():
    global player
    if player:
        player.stop()
        player = None





'''
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import os
import time
import threading

class AudioPlayer:
    def __init__(self, filepath):
        self.filepath = filepath
        self._stop_flag = threading.Event()
        self._play_thread = None

    def _play(self):
        try:
            with sf.SoundFile(self.filepath) as f:
                data = f.read(dtype='float32')
                samplerate = f.samplerate
                sd.play(data, samplerate)
                while sd.get_stream().active:
                    if self._stop_flag.is_set():
                        sd.stop()
                        break
                    time.sleep(0.1)
        except Exception as e:
            print(f"Oynatma hatası: {e}")

    def play(self):
        self._stop_flag.clear()
        self._play_thread = threading.Thread(target=self._play, daemon=True)
        self._play_thread.start()

    def stop(self):
        self._stop_flag.set()
        sd.stop()
        if self._play_thread:
            self._play_thread.join()

def metni_olustur(metin):
    gecici_klasor = '..\\temps'
    if not os.path.exists(gecici_klasor):
        os.makedirs(gecici_klasor)
    cikti_dosyasi = os.path.join(gecici_klasor, 'okunan_metin.mp3')
    tts = gTTS(text=metin, lang='tr', slow=False)
    tts.save(cikti_dosyasi)
    return cikti_dosyasi


def metni_oku(metin):
    """
    Verilen metni sese dönüştürür, oynatır ve geçici dosyayı güvenli bir şekilde siler.

    Args:
        metin (str): Sese dönüştürülecek metin.
    """
    gecici_klasor = '.\\temps'
    dil = 'tr'
    cikti_dosyasi = None
    try:
        # Geçici klasörü kontrol et, yoksa oluştur
        if not os.path.exists(gecici_klasor):
            os.makedirs(gecici_klasor)
            print(f"'{gecici_klasor}' klasörü oluşturuldu.")

        # Geçici dosya yolu oluştur
        cikti_dosyasi = os.path.join(gecici_klasor, 'okunan_metin.mp3')

        # Metni sese dönüştür ve kaydet
        print("Metin sese dönüştürülüyor...")
        tts = gTTS(text=metin, lang=dil, slow=False)
        tts.save(cikti_dosyasi)
        print(f"Ses dosyası '{cikti_dosyasi}' olarak kaydedildi.")

        # Oynatma başlamadan önce dosyanın tamamen yazıldığından emin olmak için kısa bir bekleme
        time.sleep(0.5)

        # Ses dosyasını oynat
        print("Ses dosyası oynatılıyor...")
        # 'with' bloğu kullanarak dosyanın otomatik olarak kapatılmasını sağla
        with sf.SoundFile(cikti_dosyasi) as f:
            sd.play(f.read(dtype='float32'), f.samplerate)
            sd.wait()  # Oynatma bitene kadar bekle
        print("Oynatma tamamlandı.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

    finally:
        # Oynatma işlemi bittikten ve dosyaya olan erişim serbest bırakıldıktan sonra silme işlemi
        if cikti_dosyasi and os.path.exists(cikti_dosyasi):
            try:
                os.remove(cikti_dosyasi)
                print(f"'{cikti_dosyasi}' geçici dosyası silindi.")
            except OSError as e:
                print(f"❌ Dosya silinemedi: {e}")
                print("Lütfen programın dosyaya erişimini engelleyen başka bir uygulama olup olmadığını kontrol edin.")
                '''