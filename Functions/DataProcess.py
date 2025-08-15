import json


def getQuestions() -> list:
    """
    Sabit soru listesini döndüren fonksiyon.
    """
    questions = [
        {"id": 1,
         "question": "Tozlu bir ortamda maske takmak zorundasınız. Maskenin burun teli kısmını ayarlamadan "
                     "kullanmanızın ne gibi sonuçları olur?",
         "category": "teknik_bilgi", "level": "orta"},
        {"id": 2,
         "question": "Kaynak işlemi sırasında koruyucu gözlük yerine şeffaf gözlük kullanan bir işçiyi gözlemlediniz."
                     " Bu durumun yaratabileceği tehlikeleri sıralayınız.",
         "category": "teknik_bilgi", "level": "zor"},
        {"id": 3,
         "question": "El koruması gereken bir işte kumaş eldiven yerine deri eldiven kullanmanızın doğurabileceği "
                     "sonucu açıklayınız.",
         "category": "teknik_bilgi", "level": "kolay"},
        {"id": 4,
         "question": "Gürültülü bir ortamda kulaklık kullanılmadığını gözlemlediniz. Bu ne tür bir risk oluşturur?",
         "category": "risk_tanima", "level": "kolay"},
        {"id": 5,
         "question": "Yangına dayanıklı olması gereken kıyafetlerin sentetik kumaştan yapıldığını fark ettiniz. Ne gibi sonuçlar doğabilir?",
         "category": "risk_tanima", "level": "orta"},
        {"id": 6,
         "question": "Asbestli ortamda uygun solunum koruyucusu olmadan çalışmak ne tür kalıcı sağlık sorunlarına neden olabilir?",
         "category": "risk_tanima", "level": "zor"},
        {"id": 7,
         "question": "İSG eğitimi almamış bir işçinin, bu eğitimi almadan sahada çalıştırılması yasal mıdır?",
         "category": "mevzuat", "level": "kolay"},
        {"id": 8,
         "question": "İSG eğitimi almış ancak KKD kullanmayı reddeden bir çalışanın sorumluluğu mevzuatta nasıl tanımlanır?",
         "category": "mevzuat", "level": "orta"},
        {"id": 9,
         "question": "İşveren, çalışanına KKD’yi temin ettiğini ancak kullanımını denetlemediğini savunursa, bu mevzuata göre geçerli midir?",
         "category": "mevzuat", "level": "zor"},
        {"id": 10,
         "question": "Kimyasal sıçramaya maruz kalan bir iş arkadaşınızın gözlerinde yanma hissi oluştu. İlk olarak ne yaparsınız?",
         "category": "kriz_yonetimi", "level": "senaryo"}
    ]

    # Her soru objesine boş bir "answer" anahtarı eklenir
    for q in questions:
        q["answer"] = ""

    return questions

def getAnswers(tc: str) -> dict:
    """
    Verilen JSON dosyasından {id: answer} sözlüğü döndürür.

    Args:
        tc (str): TC Kimlik numarası

    Returns:
        dict: id -> answer eşleşmelerini içeren sözlük.
    """
    filePath = f'./SavedSessions/{tc}.json'
    with open(filePath, "r", encoding="utf-8") as f:
        data = json.load(f)

    answers = {item["question"]: item["answer"] for item in data}
    return answers
