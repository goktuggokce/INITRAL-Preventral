from ollama import Client
# prompt = LLM.build_prompt(context_chunks=results, AnswerList=DataProcess.getAnswers(tc))
def RAG_build_prompt(question, context_chunks):
    context = "\n".join(context_chunks)
    prompt = f"""
    Aşağıdaki belge parçalarından anlam kaybı olmaksızın sadece soru ile alakalı olanları
    düzgün birer cümle şeklinde listele, 
    
    Belge Parçaları:
    {context}
    
    Soru: {question}
    """
    return prompt
def score_build_prompt(context_chunks, AnswerList):
    question, answer = AnswerList
    context = "\n".join(context_chunks)
    prompt = f"""Aşağıdaki belge parçaları ışığında, verilen kullanıcı cevabını değerlendir.
        📌 AMAÇ:
    Adayın verdiği cevabı değerlendir. Cevap, soruyla ne kadar örtüşüyor ve belge destekli ideal cevaba ne kadar yakın — bunu dikkate al.
    Amacın, bilmeye dayalı, belgeyle tutarlı ve mantıklı cevaplara yüksek; yetersiz veya kaçamak cevaplara düşük puan vermektir.
    
    📏 KURALLAR:
    - Cevapta bilgi yoksa (örn: "Bilmiyorum", "Unuttum", "Fikrim yok", "Emin değilim" gibi) → PUAN: 0
    - Cevap yanlış ya da belgeye aykırıysa → PUAN: 0-19
    - Cevap genel-geçer ama doğruluk şüphesi varsa → PUAN: 20-49
    - Cevap doğru ama eksik/tek boyutluysa → PUAN: 50-79
    - Cevap belgeyle uyumlu, açık ve doğruysa → PUAN: 80-99
    - Cevap belgeyle tamamen örtüşüyor, açık, eksiksiz ve netse → PUAN: 100
    
    Belge Parçaları:
    {context}
    
    Soru: {question}
    
    KULLANICI CEVABI: {answer}
    
    Lütfen bu cevabı değerlendir ve sadece 0 ile 100 arasında bir sayı olarak puan ver. Gerekirse kısa bir açıklama da ekleyebilirsin.
    Format şu şekilde olmalı:
    PUAN: <sayı>
    AÇIKLAMA: <kısa açıklama>"""
    return prompt


client = Client(host='http://localhost:11434/')  # Ollama'nın varsayılan sunucu adresi

def _clean_repetitions(text):
    lines = text.strip().split('\n')
    cleaned = []
    seen = set()

    for line in lines:
        if line.strip() not in seen:
            cleaned.append(line)
            seen.add(line.strip())

    return "\n".join(cleaned)

def generate_answer(prompt):
    print("⏳ Cevap Ollama üzerinden üretiliyor...")
    response = client.chat(
        model="qwen2.5:7b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw_answer = response['message']['content']
    answer = _clean_repetitions(raw_answer)
    print("✅ Cevap oluşturuldu.")
    return answer