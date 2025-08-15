from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import PyPDF2
import os
import pickle
import torch
import numpy as np

# embedding'leri ve FAISS index'i bir kez oluşturup hafızada saklamak için
# -------------------------
# CACHE DEĞİŞKENLERİ
# -------------------------
_cached_model = None
_cached_index = None
_cached_chunks = None

# -------------------------
# DOSYA YOLLARI
# -------------------------
FAISS_INDEX_FILE = "./cache/faiss_index.faiss"
CHUNKS_FILE = "./cache/chunks.pkl"
MODEL_CACHE_FOLDER = "./cache/model_cache"
CACHE_FOLDER = "./cache"
PDF_PATH = './Assets/Documents'


def _pdf_to_text():
    text = ""

    if not os.path.exists(PDF_PATH):
        print(f"Hata: '{PDF_PATH}' klasörü bulunamadı.")
        return text

    for filename in os.listdir(PDF_PATH):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(PDF_PATH, filename)
            try:
                with open(full_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                print(f"'{filename}' başarıyla okundu.")
            except Exception as e:
                print(f"Hata: '{filename}' dosyası okunurken bir sorun oluştu: {e}")

    return text


def _split_text(text, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)


def _load_model(model_name="e5"):
    if model_name == "e5":
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = SentenceTransformer(
            "intfloat/multilingual-e5-large",
            device=device,
            token=None,
            cache_folder=MODEL_CACHE_FOLDER
        )
        return model
    else:
        raise ValueError("Sadece 'e5' modeli desteklenmektedir.")


# Belirli bir modelle embedding üret
def _embed_texts(text_chunks, model):
    embeddings = []
    batch_size = 32
    for i in range(0, len(text_chunks), batch_size):
        batch = text_chunks[i:i + batch_size]
        print(f"Embedding çıkarılıyor: {i} - {min(i + batch_size, len(text_chunks))} / {len(text_chunks)}")
        emb = model.encode(batch, convert_to_numpy=True, normalize_embeddings=True)
        embeddings.append(emb)
    embeddings = np.vstack(embeddings)
    return embeddings.astype('float32')


# FAISS indeks oluştur
def _create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # normalize edildiği için cosine similarity
    index.add(embeddings)
    return index


def main():
    global _cached_model, _cached_index, _cached_chunks

    # 1️⃣ Eğer hafızada cache varsa direkt kullan
    if _cached_model and _cached_index and _cached_chunks:
        print("⚡ Önceden yüklenmiş model ve index hafızadan kullanılıyor.")
        return _cached_model, _cached_index, _cached_chunks

    # 2️⃣ Diskte cache dosyaları varsa yükle
    if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(CHUNKS_FILE):
        print("💾 Diskten önbellek yükleniyor...")
        model = _load_model()
        index = faiss.read_index(FAISS_INDEX_FILE)
        with open(CHUNKS_FILE, "rb") as f:
            chunks = pickle.load(f)

        _cached_model, _cached_index, _cached_chunks = model, index, chunks
        print("✅ Diskten yükleme tamam.")
        return model, index, chunks

    # 3️⃣ İlk defa çalışıyorsa PDF'leri işle
    print("📄 PDF'ler okunuyor ve embed ediliyor... (ilk çalıştırma uzun sürebilir)")
    all_text = _pdf_to_text()  # PDF'ler sadece bir kez okunuyor
    print(f"Toplam karakter sayısı: {len(all_text)}")

    all_chunks = _split_text(all_text)
    print(f"Toplam {len(all_chunks)} metin parçası bulundu.")

    model = _load_model()
    print("Model yüklendi, embedding çıkartılıyor...")
    embeddings = _embed_texts(all_chunks, model)
    print("Embedding çıkarıldı, FAISS index oluşturuluyor...")
    index = _create_faiss_index(embeddings)

    # 4️⃣ Diskte cache klasörü yoksa oluştur
    os.makedirs(CACHE_FOLDER, exist_ok=True)

    # 5️⃣ Diskte kaydet
    os.makedirs(CACHE_FOLDER, exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(all_chunks, f)

    # 6️⃣ Hafızada sakla
    _cached_model, _cached_index, _cached_chunks = model, index, all_chunks

    print("✅ Model ve index oluşturuldu, disk ve hafızaya kaydedildi.")
    return model, index, all_chunks