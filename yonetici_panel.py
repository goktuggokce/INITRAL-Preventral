import sys
import os
import json
import glob
from datetime import datetime
from typing import Dict, Any, List, Tuple

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QLineEdit, QMessageBox, QFrame, QScrollArea,
    QStackedWidget, QGridLayout, QProgressBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QHeaderView, QFileDialog, QToolBar,
    QToolButton, QDialog
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QColor

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Logging system için
import logging
from pathlib import Path

# Loglama sistemi kurulumu
REPORTS_LOGS_DIR = "reports_logs"
Path(REPORTS_LOGS_DIR).mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{REPORTS_LOGS_DIR}/admin_panel.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global ayarlar
FUSION_WEIGHTS = {"rule": 0.4, "hybrid": 0.4, "backend": 0.2}

CATEGORY_DISPLAY = {
    "teknik_bilgi": "Teknik Bilgi ve Uygulama",
    "teknik_yetkinlik": "Teknik Bilgi ve Uygulama",
    "risk_tanima": "Risk Tanıma & Hata Tespiti",
    "farkindalik": "Risk Tanıma & Hata Tespiti",
    "mevzuat": "Mevzuat Bilgisi & Yasal Haklar",
    "prosedur": "Mevzuat Bilgisi & Yasal Haklar",
    "kriz_yonetimi": "Kriz Yönetimi",
    "Karar Verme – Sorumluluk & Kriz Yönetimi": "Kriz Yönetimi",
    "Karar Verme & Kriz Yönetimi": "Kriz Yönetimi",
}


def safe_get(d: dict, path: List[str], default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def migrate_saved_sessions():
    """SavedSessions kayıtlarını yönetici paneline uygun formata çevirir"""
    logger.info("Migrating SavedSessions to admin panel format...")

    saved_sessions_dir = "SavedSessions"
    migrated_dir = "session_data"
    Path(migrated_dir).mkdir(exist_ok=True)

    if not os.path.exists(saved_sessions_dir):
        logger.warning(f"{saved_sessions_dir} directory not found")
        return

    for json_file in glob.glob(f"{saved_sessions_dir}/*.json"):
        try:
            tc = os.path.splitext(os.path.basename(json_file))[0]
            logger.info(f"Migrating {tc}")

            with open(json_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Migrate to admin panel format
            migrated_data = {
                "tc": tc,
                "start_time": datetime.fromtimestamp(os.path.getmtime(json_file)).isoformat(),
                "session_data": {
                    "tc": tc,
                    "answers": []
                },
                "overall_score": 0.0,
                "question_analysis": []
            }

            total_score = 0
            question_count = 0

            for idx, item in enumerate(session_data, 1):
                question = item.get("question", f"Soru {idx}")
                answer = item.get("answer", "")
                category = item.get("category", "genel")
                score = item.get("score", 0)
                score_desc = item.get("score_desc", "Açıklama yok.")

                # Add to answers
                migrated_data["session_data"]["answers"].append({
                    "question": question,
                    "answer": answer,
                    "category": category,
                    "score": score,
                    "score_desc": score_desc
                })

                # Add to question analysis
                migrated_data["question_analysis"].append({
                    "question": question,
                    "transcription": answer,
                    "category": category,
                    "score": score,
                    "score_desc": score_desc
                })

                total_score += score
                question_count += 1

            # Calculate overall score
            migrated_data["overall_score"] = total_score / max(1, question_count)

            # Save migrated data
            output_file = f"{migrated_dir}/{tc}_migrated.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(migrated_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Successfully migrated {tc} to {output_file}")

        except Exception as e:
            logger.error(f"Error migrating {json_file}: {e}")


class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        logger.info("LoginScreen initialized")
        self._setup()

    def _setup(self):
        logger.info("Setting up LoginScreen UI")
        self.setStyleSheet("QWidget{background:white;}")
        layout = QVBoxLayout(self)

        # Header
        header = QFrame()
        header.setStyleSheet("QFrame{background:black;color:white;padding:18px;}")
        h = QHBoxLayout(header)
        logo = QLabel()

        # Logo yolu güncellendi
        pix = QPixmap("Assets/Images/logo.png")
        if not pix.isNull():
            logo.setPixmap(pix.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo.setText("⚡")
            logo.setFont(QFont("Arial", 42))

        title = QLabel("PREVENTRAL – YÖNETİCİ RAPOR PANELİ")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color:white;")
        h.addWidget(logo)
        h.addSpacing(10)
        h.addWidget(title)
        h.addStretch()
        layout.addWidget(header)

        body = QFrame()
        b = QVBoxLayout(body)
        b.setContentsMargins(30, 20, 30, 20)

        # TC input
        tc_label = QLabel("Aday TC Kimlik Numarası")
        tc_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.tc_input = QLineEdit()
        self.tc_input.setMaxLength(11)
        self.tc_input.setPlaceholderText("11 haneli TC giriniz")
        self.tc_input.setFixedHeight(44)
        self.tc_input.setStyleSheet(
            "QLineEdit{border:2px solid #e9ecef;border-radius:8px;padding:0 12px;background:#f8f9fa;}")

        btn = QPushButton("RAPORU GÖSTER")
        btn.setFixedHeight(44)
        btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn.setStyleSheet(
            "QPushButton{background:black;color:white;border-radius:8px;} QPushButton:hover{background:#222;}")
        btn.clicked.connect(self.search_candidate)
        self.tc_input.returnPressed.connect(self.search_candidate)

        b.addWidget(tc_label)
        b.addWidget(self.tc_input)
        b.addSpacing(8)
        b.addWidget(btn)

        # Son kayıtlar tablo
        self.recent_table = QTableWidget(0, 4)
        self.recent_table.setHorizontalHeaderLabels(["TC", "Tarih & Saat", "Genel Skor", "Dosya"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.recent_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.recent_table.doubleClicked.connect(self.load_from_table)

        b.addSpacing(20)
        b.addWidget(self.recent_table)
        layout.addWidget(body)

        self._load_recent()

    def _load_recent(self):
        logger.info("Loading recent records")
        self.recent_table.setRowCount(0)

        # Tüm kayıt kaynaklarını tara
        files = []

        # session_data klasörü
        # if os.path.exists("session_data"):
        # files.extend(glob.glob("session_data/*.json"))

        # SavedSessions klasörü
        # if os.path.exists("SavedSessions"):
        # files.extend(glob.glob("SavedSessions/*.json"))

        if os.path.exists("session_data"):
            files.extend(glob.glob("session_data/*_migrated.json"))

        # outputs klasörü
        if os.path.exists("outputs"):
            files.extend(glob.glob("outputs/**/*.json", recursive=True))

        files.sort(key=os.path.getmtime, reverse=True)
        logger.info(f"Found {len(files)} record files")

        for fp in files[:100]:  # En son 100 kayıt
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # TC numarasını çıkar
                tc = self._extract_tc(data, fp)

                # Tarih bilgisini çıkar
                dt = self._extract_date(data, fp)

                # Genel skoru hesapla
                overall = self._calculate_overall_score(data)

                # Tabloya ekle
                row = self.recent_table.rowCount()
                self.recent_table.insertRow(row)

                it_tc = QTableWidgetItem(str(tc))
                it_dt = QTableWidgetItem(dt)
                it_sc = QTableWidgetItem(f"{overall:.1f}%")

                # Skor rengini ayarla
                if overall >= 70:
                    it_sc.setForeground(QColor("#27ae60"))
                elif overall >= 50:
                    it_sc.setForeground(QColor("#f39c12"))
                else:
                    it_sc.setForeground(QColor("#e74c3c"))

                it_fp = QTableWidgetItem(os.path.basename(fp))
                it_fp.setData(Qt.UserRole, fp)

                self.recent_table.setItem(row, 0, it_tc)
                self.recent_table.setItem(row, 1, it_dt)
                self.recent_table.setItem(row, 2, it_sc)
                self.recent_table.setItem(row, 3, it_fp)

            except Exception as e:
                logger.error(f"Error loading file {fp}: {e}")
                continue

    def _extract_tc(self, data, filepath):
        """Dosyadan TC numarasını çıkarır"""
        # Data içinden TC aramaya çalış
        tc = (data.get("tc") or
              safe_get(data, ["test_info", "tc_number"]) or
              safe_get(data, ["session_data", "tc"]))

        if tc:
            return str(tc)

        # Dosya adından TC çıkarmaya çalış
        filename = os.path.splitext(os.path.basename(filepath))[0]
        # Sadece rakamları al
        tc_from_filename = ''.join(filter(str.isdigit, filename))
        if len(tc_from_filename) == 11:
            return tc_from_filename

        return "Bilinmiyor"

    def _extract_date(self, data, filepath):
        """Dosyadan tarih bilgisini çıkarır"""
        # Data içinden tarih aramaya çalış
        st = (data.get("start_time") or
              safe_get(data, ["test_info", "start_time"]) or
              safe_get(data, ["session_data", "start_time"]))

        if st:
            try:
                return datetime.fromisoformat(st).strftime("%d.%m.%Y %H:%M")
            except:
                pass

        # Dosya oluşturma tarihini kullan
        return datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%d.%m.%Y %H:%M")

    def _calculate_overall_score(self, data):
        """Dosyadan genel skoru hesaplar"""
        # Mevcut overall_score varsa kullan
        overall = data.get("overall_score")
        if isinstance(overall, (int, float)):
            return float(overall)

        # question_analysis'den hesapla
        qa = data.get("question_analysis", [])
        if qa:
            scores = [q.get("score", 0) for q in qa if isinstance(q.get("score"), (int, float))]
            if scores:
                return sum(scores) / len(scores)

        # session_data/answers'dan hesapla
        answers = safe_get(data, ["session_data", "answers"], [])
        if answers:
            scores = [a.get("score", 0) for a in answers if isinstance(a.get("score"), (int, float))]
            if scores:
                return sum(scores) / len(scores)

        # SavedSessions formatı (liste)
        if isinstance(data, list):
            scores = [item.get("score", 0) for item in data if isinstance(item.get("score"), (int, float))]
            if scores:
                return sum(scores) / len(scores)

        return 0.0

    def search_candidate(self):
        tc = self.tc_input.text().strip()
        logger.info(f"Searching for candidate: {tc}")

        if len(tc) != 11 or not tc.isdigit():
            QMessageBox.warning(self, "Hata", "Geçerli 11 haneli TC giriniz.")
            return
        wait = WaitScreen(tc, parent=self.parent)
        wait.show()
        # Tüm kaynaklardan ara
        files = []

        # session_data
        # files.extend(glob.glob(f"session_data/*{tc}*.json"))

        # SavedSessions
        # files.extend(glob.glob(f"SavedSessions/{tc}.json"))
        # session_data sadece migrate edilmiş dosyaları ara
        files.extend(glob.glob(f"session_data/*{tc}*_migrated.json"))
        # outputs
        files.extend(glob.glob(f"outputs/**/*{tc}*.json", recursive=True))

        logger.info(f"Found {len(files)} files for TC {tc}")

        if not files:
            QMessageBox.information(self, "Kayıt yok", f"{tc} için kayıt bulunamadı.")
            return

        # En yeni dosyayı seç
        fp = max(files, key=os.path.getmtime)
        logger.info(f"Loading latest file: {fp}")

        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)

            # SavedSessions formatını normalize et
            if isinstance(data, list):
                data = self._normalize_saved_session(data, tc, fp)

            self.parent.show_report(data)

        except Exception as e:
            logger.error(f"Error loading {fp}: {e}")
            QMessageBox.warning(self, "Hata", f"Okuma hatası: {e}")

    def _normalize_saved_session(self, session_data, tc, filepath):
        """SavedSessions formatını normalize eder"""
        logger.info(f"Normalizing SavedSessions data for {tc}")

        normalized = {
            "tc": tc,
            "start_time": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
            "session_data": {
                "tc": tc,
                "answers": []
            },
            "question_analysis": [],
            "overall_score": 0.0
        }

        total_score = 0
        question_count = 0

        for idx, item in enumerate(session_data, 1):
            question = item.get("question", f"Soru {idx}")
            answer = item.get("answer", "")
            category = item.get("category", "genel")
            score = item.get("score", 0)

            normalized["session_data"]["answers"].append({
                "question": question,
                "answer": answer,
                "category": category,
                "score": score
            })

            normalized["question_analysis"].append({
                "question": question,
                "transcription": answer,
                "category": category,
                "score": score
            })

            total_score += score
            question_count += 1

        normalized["overall_score"] = total_score / max(1, question_count)

        return normalized

    def load_from_table(self):
        row = self.recent_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Hata", "Hiçbir satır seçilmedi.")
            return

        fp_item = self.recent_table.item(row, 3)
        if not fp_item:
            QMessageBox.warning(self, "Hata", "Seçili satır geçersiz.")
            return

        fp = fp_item.data(Qt.UserRole)
        if not fp or not os.path.exists(fp):
            QMessageBox.warning(self, "Hata", "Dosya bulunamadı.")
            return

        # JSON'u güvenli şekilde oku
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Hata", "Dosya okunamadı: JSON hatası.")
            return
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Dosya okunurken hata oluştu: {e}")
            return

        # TC bilgisini al
        tc = data.get("tc")
        if not tc:
            QMessageBox.warning(self, "Hata", "TC bilgisi bulunamadı.")
            return

        # SavedSessions klasöründe ilgili dosyayı bul
        saved_path = os.path.join("SavedSessions", f"{tc}.json")
        if os.path.exists(saved_path):
            try:
                with open(saved_path, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)

                # Score alanı var mı kontrol et
                if isinstance(saved_data, list):
                    score_exists = any(isinstance(item, dict) and "score" in item for item in saved_data)
                else:
                    score_exists = "score" in saved_data

                if score_exists:
                    print(f"{tc}.json dosyasında 'score' alanı bulundu.")
                    self.parent.show_report(data)
                else:
                    print(f"{tc}.json dosyasında 'score' alanı yok.")
                    wait = WaitScreen(tc, parent=self)
                    wait.exec_()  # artık çalışır

            except Exception as e:
                print(f"{tc}.json dosyası okunurken hata: {e}")
        else:
            print(f"{tc}.json dosyası bulunamadı.")



class WaitScreen(QDialog):
    def __init__(self, tc, parent=None):
        super().__init__(parent)
        self.tc = tc
        self.parent = parent
        self.setWindowTitle("Lütfen Bekleyiniz")
        self.setFixedSize(300, 120)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout(self)
        label = QLabel("Lütfen Bekleyiniz...\nVeriler işleniyor.")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Worker başlat
        self.worker = ScoreWorker(self.tc)
        self.worker.finished.connect(lambda: (self.parent.load_from_table(), self.accept()))
        self.worker.start()

class ScoreWorker(QThread):
    finished = pyqtSignal(dict)  # İş bittiğinde data gönder

    def __init__(self, tc):
        super().__init__()
        self.tc = tc

    def run(self):
        try:
            from Functions.Scoring import CalculateScores, save_scores_to_json
            scores = CalculateScores(self.tc)
            save_scores_to_json(self.tc, scores)
            migrate_saved_sessions()
            self.finished.emit(scores)
        except Exception as e:
            print(f"Score calculation error: {e}")
            self.finished.emit({})  # Hata olursa boş dict

class SimpleReportScreen(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        logger.info(f"ReportScreen initialized for TC: {data.get('tc', 'Unknown')}")
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)

        # --- Üst Sekme Butonları ---
        tab_buttons_layout = QHBoxLayout()
        self.btn_score = QToolButton(text="Soru Bazlı")
        self.btn_score.setCheckable(True)
        self.btn_category = QToolButton(text="Kategori Bazlı")
        self.btn_category.setCheckable(True)
        for btn in (self.btn_score, self.btn_category):
            btn.setStyleSheet("QToolButton{padding:8px 14px;}")
            tab_buttons_layout.addWidget(btn)
        layout.addLayout(tab_buttons_layout)
        # --- Sekme İçerikleri ---
        self.stack = QStackedWidget()

        # Soru bazlı grafik sekmesi
        score_tab = QWidget()
        score_layout = QVBoxLayout(score_tab)
        self._add_score_chart(score_layout)
        self.stack.addWidget(score_tab)

        # Kategori bazlı grafik sekmesi
        category_tab = QWidget()
        category_layout = QVBoxLayout(category_tab)
        self._add_category_chart(category_layout)
        self.stack.addWidget(category_tab)

        layout.addWidget(self.stack, stretch=1)

        # --- Butonların Fonksiyonları ---
        self.btn_score.clicked.connect(lambda: self._switch_tab(0))
        self.btn_category.clicked.connect(lambda: self._switch_tab(1))

        # Başlangıçta hiçbir sekme seçili olmasın
        self.stack.setCurrentIndex(-1)
        self.btn_score.setChecked(False)
        self.btn_category.setChecked(False)

        # --- Genel Skor Başlığı ---
        overall = self.data.get("overall_score", None)
        overall_label = QLabel(f"GENEL SKOR: {overall:.1f}%")
        overall_label.setFont(QFont("Arial", 16, QFont.Bold))

        # Renkli göstermek için
        if overall >= 70:
            overall_label.setStyleSheet("color:#27ae60;")  # Yeşil
        elif overall >= 50:
            overall_label.setStyleSheet("color:#f39c12;")  # Turuncu
        else:
            overall_label.setStyleSheet("color:#e74c3c;")  # Kırmızı

        layout.addWidget(overall_label)

        # Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Sorular
        questions = self.data.get('question_analysis', [])
        if not questions:
            questions = self.data.get('session_data', {}).get('answers', [])

        for i, q in enumerate(questions, 1):
            card = self._create_question_card(i, q)
            content_layout.addWidget(card)

        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=3)

        # Back button
        back_btn = QPushButton("⬅️ GERİ DÖN")
        back_btn.setStyleSheet(
            "QPushButton{background:#6c757d;color:white;padding:8px 14px;border-radius:6px;}QPushButton:hover{background:#5a6268;}")
        back_btn.clicked.connect(self.parent.show_login)
        layout.addWidget(back_btn, 0, Qt.AlignLeft)

    def _add_score_chart(self, layout):
        questions = self.data.get('question_analysis', [])
        scores = [q.get('score', 0) for q in questions]
        labels = [f"Soru {i+1}" for i in range(len(scores))]

        fig = Figure(figsize=(5, 3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        bars = ax.bar(labels, scores, color="#4e73df")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Score (%)")
        ax.set_title("Soru Bazlı Başarı Grafiği")
        ax.bar_label(bars, fmt="%.0f%%", padding=3)
        layout.addWidget(canvas)

    def _switch_tab(self, index):
        if self.stack.currentIndex() == index:
            # Aynı sekmeye tıklarsa kapat
            self.stack.setCurrentIndex(-1)
            self.btn_score.setChecked(False)
            self.btn_category.setChecked(False)
        else:
            # Yeni sekmeyi aç
            self.stack.setCurrentIndex(index)
            self.btn_score.setChecked(index == 0)
            self.btn_category.setChecked(index == 1)
    def _add_category_chart(self, layout):
        questions = self.data.get('question_analysis', [])
        category_scores = {}
        for q in questions:
            cat = q.get('category', 'Genel')
            score = q.get('score', 0)
            category_scores.setdefault(cat, []).append(score)

        categories = list(category_scores.keys())
        averages = [sum(s)/len(s) for s in category_scores.values()]

        fig = Figure(figsize=(5, 3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        bars = ax.bar(categories, averages, color="#17a2b8")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Ortalama Başarı (%)")
        ax.set_title("Kategori Bazlı Başarı")
        ax.bar_label(bars, fmt="%.1f%%", padding=3)
        layout.addWidget(canvas)
    def _create_question_card(self, idx, question_data):
        frame = QFrame()
        frame.setStyleSheet("QFrame{border:2px solid #eee;border-radius:10px;padding:14px;}")
        layout = QVBoxLayout(frame)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel(f"SORU {idx}")
        title.setFont(QFont("Arial", 13, QFont.Bold))

        category = question_data.get('category', 'Genel')
        cat_label = QLabel(f"Kategori: {category}")
        cat_label.setStyleSheet("color:#666;")

        score = question_data.get('score', 0)
        score_label = QLabel(f"{score:.0f}%")
        score_label.setFont(QFont("Arial", 14, QFont.Bold))

        if score >= 80:
            score_label.setStyleSheet("color:#28a745;")
        elif score >= 70:
            score_label.setStyleSheet("color:#ffc107;")
        elif score >= 60:
            score_label.setStyleSheet("color:#fd7e14;")
        else:
            score_label.setStyleSheet("color:#dc3545;")

        header_layout.addWidget(title)
        header_layout.addWidget(cat_label)
        header_layout.addStretch()
        header_layout.addWidget(score_label)

        # Question
        q_label = QLabel("SORU:")
        q_label.setFont(QFont("Arial", 10, QFont.Bold))
        q_text = QTextEdit()
        q_text.setReadOnly(True)
        q_text.setMaximumHeight(90)
        q_text.setStyleSheet("QTextEdit{background:#f8f9fa;border:1px solid #ddd;border-radius:6px;}")
        q_text.setPlainText(question_data.get('question', ''))

        # Answer
        a_label = QLabel("ADAY CEVABI:")
        a_label.setFont(QFont("Arial", 10, QFont.Bold))
        a_text = QTextEdit()
        a_text.setReadOnly(True)
        a_text.setMaximumHeight(90)
        a_text.setStyleSheet(
            "QTextEdit{background:#fff3cd;border:1px solid #ffeaa7;border-radius:6px;font-weight:bold;}")
        answer = question_data.get('answer', '') or question_data.get('transcription', '')
        a_text.setPlainText(str(answer))

        # Description
        d_label = QLabel("AÇIKLAMA:")
        d_label.setFont(QFont("Arial", 10, QFont.Bold))
        d_text = QTextEdit()
        d_text.setReadOnly(True)
        d_text.setMaximumHeight(90)
        d_text.setStyleSheet("QTextEdit{background:#f8f9fa;border:1px solid #ddd;border-radius:6px;}")
        d_text.setPlainText(question_data.get('score_desc', ''))

        layout.addLayout(header_layout)
        layout.addWidget(q_label)
        layout.addWidget(q_text)
        layout.addWidget(a_label)
        layout.addWidget(a_text)
        layout.addWidget(d_label)
        layout.addWidget(d_text)

        return frame


class YoneticiPanelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("YoneticiPanelApp initialized")
        self.setWindowTitle("PREVENTRAL - Yönetici Rapor Paneli")
        self.setGeometry(50, 50, 1600, 1000)
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        self.login = LoginScreen(self)
        self.stacked.addWidget(self.login)
        self.setStyleSheet("QMainWindow{background:white;} QWidget{background:white;}")

    def show_report(self, data):
        logger.info(f"Showing report for TC: {data.get('tc', 'Unknown')}")
        screen = SimpleReportScreen(data, self)
        # Eski rapor ekranlarını temizle
        while self.stacked.count() > 1:
            w = self.stacked.widget(1)
            self.stacked.removeWidget(w)
            w.deleteLater()
        self.stacked.addWidget(screen)
        self.stacked.setCurrentWidget(screen)

    def show_login(self):
        logger.info("Returning to login screen")
        self.stacked.setCurrentWidget(self.login)
        # Listeyi yenile
        self.login._load_recent()


def main():
    # High DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("PREVENTRAL Yönetici Paneli")
    app.setApplicationVersion("2.0.0")

    logger.info("Starting PREVENTRAL Admin Panel v2.0.0")

    # Mevcut kayıtları migrate et
    try:
        migrate_saved_sessions()
    except Exception as e:
        logger.error(f"Migration error: {e}")

    win = YoneticiPanelApp()
    win.show()

    # Merkeze al
    screen = app.desktop().screenGeometry()
    size = win.geometry()
    win.move(int((screen.width() - size.width()) / 2),
             int((screen.height() - size.height()) / 2))

    logger.info("Admin panel window shown")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
