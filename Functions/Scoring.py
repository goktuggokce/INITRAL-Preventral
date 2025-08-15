from . import LLMProcess
from . import DataProcess
from . import RAGProcess
import json
import os
import re

# 🎯 Kullanıcı cevabını puanla
def CalculateScores(tc: str):
    score_results = {}
    for question, answer in DataProcess.getAnswers(tc).items():
        AnswerList = (question, answer)

        # context_chunks al (RAGProcess üzerinden)
        context_chunks = RAGProcess.get_context_chunks(question, top_k=5, threshold=0.8)

        # prompt oluştur
        prompt = LLMProcess.score_build_prompt(context_chunks=context_chunks, AnswerList=AnswerList)

        # LLM'den cevap al
        score = LLMProcess.generate_answer(prompt)

        # Sonucu kaydet
        score_results[question] = score
    return score_results


def save_scores_to_json(tc: str, scores: dict, folder_path: str = "SavedSessions"):
    """
    tc: kişinin T.C. numarası (dosya ismi)
    scores: {question: score_text} dict'i, örn: "PUAN: 85\nAÇIKLAMA: ...."
    folder_path: JSON dosyalarının bulunduğu klasör
    """
    file_path = os.path.join(folder_path, f"{tc}.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} bulunamadı.")

    # Mevcut JSON'u oku
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Her soruya skor ekle
    for item in data:
        question = item.get("question")
        if question in scores:
            full_score_text = scores[question]

            # PUAN ve AÇIKLAMA ayır
            puan_match = re.search(r"PUAN:\s*(\d+)", full_score_text)
            desc_match = re.search(r"AÇIKLAMA:\s*(.*)", full_score_text, re.DOTALL)

            item["score"] = int(puan_match.group(1)) if puan_match else None
            item["score_desc"] = desc_match.group(1).strip() if desc_match else None

    # Güncellenmiş JSON'u tekrar kaydet
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return True