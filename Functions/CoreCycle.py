from . import DataProcess, TextToSpeech, SpeechToText, RAGProcess, Scoring

import json
import os


class CoreCycleManager:
    def __init__(self, tc: str):
        self.tc = tc
        self.questions_and_answers = DataProcess.getQuestions()
        self.current_question_index = 0
        self.total_questions = len(self.questions_and_answers)

        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.SAVED_SESSIONS_DIR = os.path.join(BASE_DIR, 'SavedSessions')
        os.makedirs(self.SAVED_SESSIONS_DIR, exist_ok=True)

    def get_current_question_data(self):
        if 0 <= self.current_question_index < self.total_questions:
            return self.questions_and_answers[self.current_question_index]
        return None

    def get_question_status_text(self):
        return f"Soru {self.current_question_index + 1} / {self.total_questions}"

    def get_question_text(self):
        q_data = self.get_current_question_data()
        if q_data:
            return q_data.get('question', '')
        return ""

    def speak_current_question(self):
        q_text = self.get_question_text()
        if q_text:
            self.audio_file = TextToSpeech.metni_olustur(q_text)
            if hasattr(self, 'audio_player'):
                self.audio_player.stop()
            self.audio_player = TextToSpeech.AudioPlayer(self.audio_file)
            self.audio_player.play()

    def save_answers(self):
        if not os.path.exists(self.SAVED_SESSIONS_DIR):
            os.makedirs(self.SAVED_SESSIONS_DIR, exist_ok=True)
        filePath = os.path.join(self.SAVED_SESSIONS_DIR, f'{self.tc}.json')
        with open(filePath, 'w', encoding='utf-8') as f:
            json.dump(self.questions_and_answers, f, ensure_ascii=False, indent=4)

    def next_question(self):
        if self.current_question_index < self.total_questions - 1:
            self.current_question_index += 1
            return True
        return False

    def prev_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            return True
        return False

    def voice_answer_current_question(self):
        try:
            print("Sesli cevap alma başladı...")
            answer_text = SpeechToText.transcribe_from_mic().strip()
            print(f"Algılanan sesli cevap: {answer_text}")
            return answer_text
        except Exception as e:
            return f"Sesli cevap alınırken hata oluştu: {e}", ""

    def answer_current_question(self, answer_text: str):
        q_data = self.get_current_question_data()
        if q_data is None:
            return "Geçerli soru bulunamadı."

        q_data['answer'] = answer_text
        return "Cevap kaydedildi."