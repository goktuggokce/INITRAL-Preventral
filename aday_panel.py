import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTextEdit,
                             QLineEdit, QMessageBox, QProgressBar, QFrame,
                             QStackedWidget, QSizePolicy, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QRegExp
from PyQt5.QtGui import QFont, QPixmap, QRegExpValidator

from Functions import DataProcess, CoreCycle, SpeechToText, TextToSpeech
import time

# DOSYA YOLLARI
LOGO_PATH = "Assets/Images/logo.png"


#

class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("BEKLEYİNİZ")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(label)
        self.setLayout(layout)


class ModelLoaderThread(QThread):
    model_loaded = pyqtSignal()

    def run(self):
        SpeechToText.get_model()
        self.model_loaded.emit()


class ResponseModeScreen(QWidget):
    mode_selected = pyqtSignal(str, str)  # tc_number, mode

    def __init__(self, tc_number: str):
        super().__init__()
        self.tc_number = tc_number
        self.mode_group = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Header
        header_container = QFrame()
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        logo_pixmap = QPixmap(LOGO_PATH)
        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("🏢")
            logo_label.setFont(QFont("Arial", 40))
        logo_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("PREVENTRAL")
        title_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: black; margin-left: 15px;")

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_container.setLayout(header_layout)

        subtitle_label = QLabel("CEVAP VERME ŞEKLİNİ SEÇİNİZ")
        subtitle_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #333; margin-bottom: 30px;")

        # Mode selection form
        form_frame = QFrame()
        form_frame.setMaximumWidth(500)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid black;
                border-radius: 10px;
                padding: 40px;
            }
        """)

        form_layout = QVBoxLayout()

        # User info
        user_info_label = QLabel(f"Aday: {self.tc_number}")
        user_info_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        user_info_label.setAlignment(Qt.AlignCenter)
        user_info_label.setStyleSheet("color: #666; margin-bottom: 20px;")

        # Mode selection
        self.mode_group = QButtonGroup()

        voice_radio = QRadioButton("🎤 Sesli Cevap Vermek İstiyorum")
        voice_radio.setFont(QFont("Arial", 14))
        voice_radio.setStyleSheet("""
            QRadioButton {
                padding: 15px;
                margin: 10px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)

        text_radio = QRadioButton("✏️ Yazılı Cevap Vermek İstiyorum")
        text_radio.setFont(QFont("Arial", 14))
        text_radio.setStyleSheet("""
            QRadioButton {
                padding: 15px;
                margin: 10px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)

        self.mode_group.addButton(voice_radio, 0)
        self.mode_group.addButton(text_radio, 1)
        voice_radio.setChecked(True)  # Default selection

        continue_btn = QPushButton("DEVAM ET")
        continue_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        continue_btn.setMinimumHeight(50)
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover { background-color: #333; }
        """)
        continue_btn.clicked.connect(self._on_continue_clicked)

        form_layout.addWidget(user_info_label)
        form_layout.addWidget(voice_radio)
        form_layout.addWidget(text_radio)
        form_layout.addWidget(continue_btn)
        form_frame.setLayout(form_layout)

        layout.addWidget(header_container)
        layout.addWidget(subtitle_label)
        layout.addWidget(form_frame, 0, Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def _on_continue_clicked(self):
        selected_id = self.mode_group.checkedId()
        mode = "voice" if selected_id == 0 else "text"
        self.mode_selected.emit(self.tc_number, mode)


class LoginScreen(QWidget):
    login_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.tc_input = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Header (logo + başlık)
        header_container = QFrame()
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        logo_pixmap = QPixmap(LOGO_PATH)
        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("🏢")
            logo_label.setFont(QFont("Arial", 40))
        logo_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("PREVENTRAL")
        title_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: black; margin-left: 15px;")

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.setSpacing(10)
        header_container.setLayout(header_layout)
        header_container.setStyleSheet("margin: 30px;")

        subtitle_label = QLabel("ADAY DEĞERLENDİRME PANELİ")
        subtitle_label.setFont(QFont("Arial", 16))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; margin-bottom: 40px;")

        # Form
        form_frame = QFrame()
        form_frame.setMaximumWidth(400)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid black;
                border-radius: 10px;
                padding: 30px;
            }
        """)

        form_layout = QVBoxLayout()

        tc_label = QLabel("TC Kimlik Numarası:")
        tc_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.tc_input = QLineEdit()
        self.tc_input.setFont(QFont("Arial", 14))
        self.tc_input.setMaxLength(11)
        self.tc_input.setPlaceholderText("11 haneli TC numaranızı giriniz")

        # TC Validator - sadece rakam, tam 11 karakter
        tc_validator = QRegExpValidator(QRegExp("[0-9]{0,11}"))
        self.tc_input.setValidator(tc_validator)

        # Enter tuşu ile giriş yapabilme
        self.tc_input.returnPressed.connect(self._handle_login)

        self.tc_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: black;
            }
            QLineEdit:invalid {
                border-color: red;
            }
        """)

        login_btn = QPushButton("GİRİŞ YAP")
        login_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        login_btn.setMinimumHeight(45)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #333; }
        """)
        login_btn.clicked.connect(self._handle_login)

        form_layout.addWidget(tc_label)
        form_layout.addWidget(self.tc_input)
        form_layout.addSpacing(20)
        form_layout.addWidget(login_btn)
        form_frame.setLayout(form_layout)

        layout.addWidget(header_container)
        layout.addWidget(subtitle_label)
        layout.addWidget(form_frame, 0, Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def _handle_login(self):
        """Validate TC number and proceed with login"""
        tc_number = self.tc_input.text().strip()

        # Check if TC number is exactly 11 digits
        if len(tc_number) != 11:
            QMessageBox.warning(
                self,
                "Geçersiz TC Kimlik Numarası",
                "TC Kimlik Numarası tam olarak 11 rakamdan oluşmalıdır.",
                QMessageBox.Ok
            )
            return

        # Check if TC number contains only digits
        if not tc_number.isdigit():
            QMessageBox.warning(
                self,
                "Geçersiz TC Kimlik Numarası",
                "TC Kimlik Numarası sadece rakamlardan oluşmalıdır.",
                QMessageBox.Ok
            )
            return

        # Check if TC number doesn't start with 0
        if tc_number.startswith('0'):
            QMessageBox.warning(
                self,
                "Geçersiz TC Kimlik Numarası",
                "TC Kimlik Numarası 0 ile başlayamaz.",
                QMessageBox.Ok
            )
            return

        # If all validations pass, emit login signal
        self.login_requested.emit(tc_number)


class AssessmentScreen(QWidget):
    return_to_login_signal = pyqtSignal()  # Signal to return to login screen

    def __init__(self, tc_number: str, response_mode: str = "voice"):
        super().__init__()
        self.tc_number = tc_number
        self.response_mode = response_mode  # "voice" or "text"
        self.core_cycle = CoreCycle.CoreCycleManager(tc_number)
        self.answer_thread = None
        self.speak_thread = None
        self.repeat_cooldown_timer = QTimer()
        self.repeat_cooldown_timer.setSingleShot(True)
        self.repeat_cooldown_timer.timeout.connect(self._enable_repeat_btn)
        self.recording_animation_timer = QTimer()
        self.recording_animation_timer.setSingleShot(True)
        self.recording_animation_timer.timeout.connect(self._recording_finished)
        self.current_question = 0
        self.questions = []
        self.question_title = None
        self.question_text = None
        self.status_label = None
        self.repeat_btn = None
        self.next_btn = None
        self.prev_btn = None
        self.record_btn = None
        self.progress_bar = None
        self.answer_input = None  # For text mode
        self.analysis_in_progress = False  # Track if answer analysis is ongoing

        # Exam Timer - 20 minutes (1200 seconds)
        self.exam_timer = QTimer()
        self.exam_timer.timeout.connect(self._handle_timeout)
        self.exam_duration = 20 * 60  # 20 minutes in seconds
        self.remaining_time = self.exam_duration
        self.timer_display = None

        # Update timer every second
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self._update_timer_display)
        self.display_timer.start(1000)  # Update every 1 second

        self._build_ui()
        self._getQuestions()
        self._show_current_question()

        # Start the exam timer
        self._start_exam_timer()

    def _build_ui(self):
        layout = QVBoxLayout()

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: black; color: white; padding: 15px;")
        header_layout = QHBoxLayout()

        header_logo_label = QLabel()
        header_logo_pixmap = QPixmap(LOGO_PATH)
        if not header_logo_pixmap.isNull():
            scaled_header_logo = header_logo_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            header_logo_label.setPixmap(scaled_header_logo)
        else:
            header_logo_label.setText("🏢")
            header_logo_label.setFont(QFont("Arial", 20))
        header_logo_label.setStyleSheet("color: white;")

        title_label = QLabel("PREVENTRAL DEĞERLENDİRME")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; margin-left: 10px;")

        logo_title_container = QWidget()
        logo_title_layout = QHBoxLayout()
        logo_title_layout.setContentsMargins(0, 0, 0, 0)
        logo_title_layout.addWidget(header_logo_label)
        logo_title_layout.addWidget(title_label)
        logo_title_layout.setSpacing(5)
        logo_title_container.setLayout(logo_title_layout)

        info_label = QLabel(f"Aday: {self.tc_number}")
        info_label.setFont(QFont("Arial", 12))
        info_label.setStyleSheet("color: white;")

        # Timer display
        self.timer_display = QLabel("⏰ 20:00")
        self.timer_display.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.timer_display.setStyleSheet(
            "color: white; background-color: #dc3545; padding: 8px 12px; border-radius: 5px; margin-left: 10px;")

        header_layout.addWidget(logo_title_container)
        header_layout.addStretch()
        header_layout.addWidget(info_label)
        header_layout.addWidget(self.timer_display)
        header_frame.setLayout(header_layout)

        # Question area
        self.question_frame = QFrame()
        self.question_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid black;
                border-radius: 10px;
                margin: 20px;
                padding: 30px;
            }
        """)

        question_layout = QVBoxLayout()

        self.question_title = QLabel("")
        self.question_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.question_title.setAlignment(Qt.AlignCenter)
        self.question_title.setStyleSheet("color: black; margin-bottom: 20px;")

        self.question_text = QTextEdit()
        self.question_text.setFont(QFont("Arial", 14))
        self.question_text.setMaximumHeight(150)
        self.question_text.setReadOnly(True)
        self.question_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
            }
        """)

        # Controls
        buttons = QHBoxLayout()

        # Set button text and icon based on mode
        if self.response_mode == "voice":
            button_text = "🎤 CEVAPLA"
        else:
            button_text = "✏️ CEVABI KAYDET"

        self.record_btn = QPushButton(button_text)
        self.record_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.record_btn.setMinimumHeight(60)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border: 2px solid black;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
            }
            QPushButton:hover:!disabled {
                background-color: #333;
            }
            QPushButton:disabled {
                background-color: #555;
                border-color: #555;
                color: #ccc;
            }
            """)
        self.record_btn.clicked.connect(self._handle_record_btn)

        self.next_btn = QPushButton("⏭️ SONRAKİ SORU")
        self.next_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.next_btn.setMinimumHeight(50)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2; color: white; border: 2px solid #1976D2;
                border-radius: 8px; padding: 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)
        self.next_btn.clicked.connect(self._go_to_next_question)

        self.prev_btn = QPushButton("⏮️ ÖNCEKİ SORU")
        self.prev_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.prev_btn.setMinimumHeight(50)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: 2px solid #1976D2;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
            }
            QPushButton:hover:!disabled {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #999999;
                border-color: #999999;
                color: #cccccc;
            }
        """)
        self.prev_btn.clicked.connect(self._go_to_prev_question)

        self.repeat_btn = QPushButton("🔄 TEKRAR OKU")
        self.repeat_btn.setFont(QFont("Arial", 14))
        self.repeat_btn.setMinimumHeight(50)
        self.repeat_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 2px solid #4CAF50;
                        border-radius: 8px;
                        padding: 10px;
                        font-weight: bold;
                    }

                    QPushButton:hover:!disabled {
                        background-color: #333;
                    }
                    QPushButton:disabled {
                        background-color: #555;
                        border-color: #555;
                        color: #ccc;
                    }
                """)
        self.repeat_btn.clicked.connect(self._handle_repeat_btn)

        buttons.addWidget(self.record_btn)
        buttons.addWidget(self.repeat_btn)
        buttons.addWidget(self.prev_btn)
        buttons.addWidget(self.next_btn)

        # Status + Progress (yalnız görünüm)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid black; border-radius: 5px;
                text-align: center; font-weight: bold;
            }
            QProgressBar::chunk { background-color: #dc3545; border-radius: 3px; }
        """)

        self.status_label = QLabel("Kategori bilgisi burada gösterilir.")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; margin: 10px;")

        question_layout.addWidget(self.question_title)
        question_layout.addWidget(self.question_text)
        # Answer input area (for text mode)
        if self.response_mode == "text":
            self.answer_input = QTextEdit()
            self.answer_input.setFont(QFont("Arial", 12))
            self.answer_input.setMaximumHeight(120)
            self.answer_input.setPlaceholderText("Cevabınızı buraya yazınız...")
            self.answer_input.setStyleSheet("""
                        QTextEdit {
                            background-color: white;
                            border: 2px solid #ddd;
                            border-radius: 5px;
                            padding: 15px;
                        }
                        QTextEdit:focus {
                            border-color: black;
                        }
                    """)
            question_layout.addWidget(self.answer_input)
        question_layout.addSpacing(20)
        question_layout.addLayout(buttons)
        question_layout.addWidget(self.progress_bar)
        question_layout.addWidget(self.status_label)
        self.question_frame.setLayout(question_layout)

        # Footer
        footer_frame = QFrame()
        footer_frame.setStyleSheet("QFrame { border-top: 1px solid #eee; }")
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(20, 8, 20, 12)
        footer_layout.setSpacing(10)

        exit_btn = QPushButton("⏻ Çıkış")
        exit_btn.setFont(QFont("Arial", 11))
        exit_btn.setMinimumHeight(32)
        exit_btn.clicked.connect(QApplication.quit)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2; color: white; border: 1px solid #1976D2;
                border-radius: 6px; padding: 6px 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)

        footer_layout.addStretch()
        footer_layout.addWidget(exit_btn)
        footer_frame.setLayout(footer_layout)

        layout.addWidget(header_frame)
        layout.addWidget(self.question_frame)
        layout.addStretch()
        layout.addWidget(footer_frame)
        self.setLayout(layout)

    def _start_speaking(self):
        if self.speak_thread is not None and self.speak_thread.isRunning():
            self.speak_thread.stop()
            self.speak_thread.wait()

        self.speak_thread = SpeakThread(self.core_cycle)
        self.speak_thread.start()

    def _stop_speaking(self):
        if self.speak_thread is not None and self.speak_thread.isRunning():
            self.speak_thread.stop()
            self.speak_thread.wait()

        # Ek güvenlik için tüm ses kaynaklarını durdur

        TextToSpeech.tts_durdur()

        # CoreCycle audio player'ı durdur
        if hasattr(self.core_cycle, 'audio_player') and self.core_cycle.audio_player:
            self.core_cycle.audio_player.stop()

        # sounddevice durdur
        try:
            import sounddevice as sd
            sd.stop()
        except:
            pass

    def _enable_repeat_btn(self):
        # Only enable repeat button if analysis is not in progress
        if not self.analysis_in_progress:
            self.repeat_btn.setEnabled(True)

    def _update_navigation_buttons(self):
        """Update navigation buttons based on analysis state"""
        if self.analysis_in_progress:
            # Disable navigation and repeat button during analysis
            self.next_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.repeat_btn.setEnabled(False)
        else:
            # Enable navigation when analysis is complete
            self.next_btn.setEnabled(True)
            # Only enable prev button if not on first question
            self.prev_btn.setEnabled(self.core_cycle.current_question_index > 0)
            self.repeat_btn.setEnabled(True)

    def _show_current_question(self):
        q_data = self.core_cycle.get_current_question_data()
        if not q_data:
            return
        self.question_title.setText(self.core_cycle.get_question_status_text())
        self.question_text.setText(self.core_cycle.get_question_text())

        category_names = {
            "teknik_bilgi": "Teknik Bilgi ve Uygulama",
            "risk_tanima": "Risk Tanıma ve Hata Tespiti",
            "mevzuat": "Mevzuat Bilgisi ve Yasal Haklar",
            "kriz_yonetimi": "Karar Verme, Sorumluluk ve Kriz Yönetimi"
        }
        category = category_names.get(q_data.get("category", "genel"), "Genel")
        level = q_data.get("level", "").upper()
        self.status_label.setText(f"Kategori: {category} | Seviye: {level}")

        self.record_btn.setEnabled(True)
        self._update_navigation_buttons()  # Use centralized button management

        if self.core_cycle.current_question_index == self.core_cycle.total_questions - 1:
            self.next_btn.setText("🏁 SINAVI BİTİR")
        else:
            self.next_btn.setText("⏭️ SONRAKİ SORU")

        # Thread ile soruyu okut
        self._start_speaking()

    def _handle_record_btn(self):
        # TTS sesi varsa durdur - daha agresif yaklaşım
        self._stop_speaking()

        TextToSpeech.tts_durdur()

        # CoreCycle içindeki audio_player'ı da durdur
        if hasattr(self.core_cycle, 'audio_player') and self.core_cycle.audio_player:
            self.core_cycle.audio_player.stop()

        # Genel ses durdurma - sounddevice kullanıyorsa
        try:
            import sounddevice as sd
            sd.stop()
        except:
            pass

        if self.response_mode == "text":
            # Text mode - get answer from text input
            answer_text = self.answer_input.toPlainText().strip()
            if not answer_text:
                QMessageBox.warning(self, "Uyarı", "Lütfen cevabınızı yazınız.")
                return

            # Process text answer
            self.record_btn.setEnabled(False)
            self.record_btn.setText("Kaydediliyor...")

            # Save answer and continue
            self.core_cycle.answer_current_question(answer_text)
            self._on_answer_finished(result=answer_text)

        else:
            # Voice mode - existing functionality
            self.record_btn.setEnabled(False)
            self.analysis_in_progress = True  # Set analysis flag
            self._update_navigation_buttons()  # Disable navigation

            self.answer_thread = AnswerThread(self.core_cycle, self.response_mode)
            self.answer_thread.started_recording_signal.connect(lambda text: self.record_btn.setText(text))
            self.answer_thread.started_analysis_signal.connect(lambda text: self.record_btn.setText(text))
            self.answer_thread.finished_signal.connect(self._on_answer_finished)
            self.answer_thread.start()

    def _on_started_analysis(self):
        self.record_btn.setText("Analiz Yapılıyor...")

    def _on_answer_finished(self, result):
        # Analysis completed, re-enable navigation
        self.analysis_in_progress = False
        self._update_navigation_buttons()

        # Kayıt animasyonu bitmeden önce "Kayıt Edildi" göster
        self.record_btn.setText("Kayıt Edildi")
        # 2 saniye bekleyip sonra devam et
        self.recording_animation_timer.start(2000)
        # İstersen sonuç mesajı gösterme veya console'a yazdırabilirsin
        print(f"Cevap sonucu: {result}")

    def _recording_finished(self):
        # Animasyon bitince butonu tekrar aktif et ve metni sıfırla
        if self.response_mode == "voice":
            self.record_btn.setText("🎤 CEVAPLA")
        else:
            self.record_btn.setText("✏️ CEVABI KAYDET")
            # Text mode'da input'u temizle
            if self.answer_input:
                self.answer_input.clear()

        self.record_btn.setEnabled(True)

        # Sonraki soruya otomatik geç
        if not self.core_cycle.next_question():
            # Tüm sorular bitince durumu güncelle ve cevapları kaydet
            self.question_title.setText("DEĞERLENDİRME TAMAMLANDI")
            self.question_text.setText("✅ Tüm sorular cevaplandı ve kayıt edildi.")
            self.prev_btn.setEnabled(False)
            self.record_btn.setEnabled(False)
            self.repeat_btn.setEnabled(False)
            self.core_cycle.save_answers()
        else:
            # Yeni soruyu göster
            self._show_current_question()

    def _handle_repeat_btn(self):
        # Don't allow repeat during analysis
        if self.analysis_in_progress:
            return

        self.repeat_btn.setEnabled(False)  # Butonu pasif yap
        self._start_speaking()  # Ses oynatmayı başlat
        self.repeat_cooldown_timer.start(5000)  # 5 saniye (5000 ms) sonra tekrar aktif et

    def _getQuestions(self):
        self.questions = DataProcess.getQuestions()
        return

    def _go_to_next_question(self):
        # Don't allow navigation during analysis
        if self.analysis_in_progress:
            return

        self._stop_speaking()  # Sesli okuma varsa durdur

        TextToSpeech.tts_durdur()  # TTS sesini durdur

        # Check if this is the last question (exam finish case)
        if self.core_cycle.current_question_index == self.core_cycle.total_questions - 1:
            # Show confirmation dialog for finishing exam
            reply = QMessageBox.question(
                self,
                "Sınav Bitir",
                "Sınavı bitirip sistemden çıkmak istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Stop timers
                self.exam_timer.stop()
                self.display_timer.stop()

                # Stop all audio playback immediately
                self._stop_speaking()

                TextToSpeech.tts_durdur()

                # Save answers and show confirmation
                self.core_cycle.save_answers()

                # Show save confirmation message
                QMessageBox.information(
                    self,
                    "Sınav Tamamlandı",
                    "Cevaplarınız kaydedildi. Teşekkür ederiz.",
                    QMessageBox.Ok
                )

                # Stop audio again just to be sure
                TextToSpeech.tts_durdur()
                # Redirect to login screen
                self._return_to_login()
            # If No is clicked, do nothing (stay on current question)
            return

        if self.core_cycle.next_question():
            self._show_current_question()
        else:
            self.question_title.setText("DEĞERLENDİRME TAMAMLANDI")
            self.question_text.setText("✅ Tüm sorular görüntülendi.")
            self.next_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.record_btn.setEnabled(False)
            self.repeat_btn.setEnabled(False)

    def _go_to_prev_question(self):
        # Don't allow navigation during analysis
        if self.analysis_in_progress:
            return

        if self.core_cycle.prev_question():
            self._show_current_question()
        else:
            # İlk sorudayız, geri gidilemez
            pass

    def _return_to_login(self):
        """Return to login screen after exam completion"""
        # Stop timers
        if hasattr(self, 'exam_timer'):
            self.exam_timer.stop()
        if hasattr(self, 'display_timer'):
            self.display_timer.stop()

        # Ensure all audio is stopped before returning to login
        self._stop_speaking()

        TextToSpeech.tts_durdur()

        self.return_to_login_signal.emit()

    def _start_exam_timer(self):
        """Start the 20-minute exam timer"""
        self.exam_timer.start(self.exam_duration * 1000)  # Convert to milliseconds
        print(f"🕐 Sınav başladı! Süre: {self.exam_duration // 60} dakika")

    def _update_timer_display(self):
        """Update the timer display every second"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60

            # Change color when time is running low
            if self.remaining_time <= 300:  # Last 5 minutes
                color = "#ff4444"  # Red
            elif self.remaining_time <= 600:  # Last 10 minutes
                color = "#ff8800"  # Orange
            else:
                color = "#dc3545"  # Default red

            self.timer_display.setText(f"⏰ {minutes:02d}:{seconds:02d}")
            self.timer_display.setStyleSheet(
                f"color: white; background-color: {color}; padding: 8px 12px; border-radius: 5px; margin-left: 10px;")
        else:
            self._handle_timeout()

    def _handle_timeout(self):
        """Handle exam timeout - save answers and redirect"""
        # Stop all timers
        self.exam_timer.stop()
        self.display_timer.stop()

        # Stop any ongoing processes
        self._stop_speaking()

        TextToSpeech.tts_durdur()

        # Stop analysis if in progress
        self.analysis_in_progress = False

        # Save current answers
        self.core_cycle.save_answers()

        # Show timeout message
        QMessageBox.information(
            self,
            "Süre Doldu",
            "Zamanınız bitti! Bu süreye kadar verdiğiniz cevaplar kaydedildi.",
            QMessageBox.Ok
        )

        # Return to login screen
        self._return_to_login()


class AdayPanelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PREVENTRAL - Aday Değerlendirme Paneli")
        self.setGeometry(100, 100, 1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Loading ekranı
        self.loading_screen = LoadingScreen()
        self.login_screen = LoginScreen()
        self.login_screen.login_requested.connect(self.start_assessment)

        self.stacked_widget.addWidget(self.loading_screen)
        self.stacked_widget.addWidget(self.login_screen)

        # Önce loading ekranını göster
        self.stacked_widget.setCurrentWidget(self.loading_screen)

        # Model yükleme thread'i başlat
        self.model_loader_thread = ModelLoaderThread()
        self.model_loader_thread.model_loaded.connect(self._on_model_loaded)
        self.model_loader_thread.start()

        self._apply_styles()

    def _on_model_loaded(self):
        # Model yüklendi, giriş ekranını göster
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: white; }
            QWidget { background-color: white; }
        """)

    def start_assessment(self, tc_number: str):
        # Show response mode selection screen
        response_mode_screen = ResponseModeScreen(tc_number or "00000000000")
        response_mode_screen.mode_selected.connect(self.start_assessment_with_mode)
        self.stacked_widget.addWidget(response_mode_screen)
        self.stacked_widget.setCurrentWidget(response_mode_screen)

    def start_assessment_with_mode(self, tc_number: str, mode: str):
        assessment_screen = AssessmentScreen(tc_number, mode)
        assessment_screen.return_to_login_signal.connect(self._return_to_login)
        self.stacked_widget.addWidget(assessment_screen)
        self.stacked_widget.setCurrentWidget(assessment_screen)

    def _return_to_login(self):
        """Return to login screen and clean up assessment screens"""
        # Reset TC input on login screen
        if hasattr(self.login_screen, 'tc_input') and self.login_screen.tc_input:
            self.login_screen.tc_input.clear()

        # Remove all screens except loading and login
        while self.stacked_widget.count() > 2:
            widget = self.stacked_widget.widget(2)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()

        # Show login screen
        self.stacked_widget.setCurrentWidget(self.login_screen)


class AnswerThread(QThread):
    started_recording_signal = pyqtSignal(str)
    started_analysis_signal = pyqtSignal(str)  # Eklenen  satır
    # finished_signal = pyqtSignal(str)  # answer_text
    finished_signal = pyqtSignal(object, str)

    def __init__(self, core_cycle, response_mode="voice"):
        super().__init__()
        self.core_cycle = core_cycle
        self.response_mode = response_mode

    def run(self):
        #  1️⃣ Kaydediliyor..
        self.started_recording_signal.emit("Kaydediliyor..")
        time.sleep(0.05)
        # Sesli cevap alma
        answer_text = self.core_cycle.voice_answer_current_question()  # kayıt süreci

        self.started_analysis_signal.emit("Analiz ediliyor..")
        # Analiz işlemi
        result = self.core_cycle.answer_current_question(answer_text)

        time.sleep(2)

        self.finished_signal.emit(result, answer_text)
        time.sleep(2)


class SpeakThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, core_cycle):
        super().__init__()
        self.core_cycle = core_cycle
        self._running = True

    def run(self):
        self._running = True
        self.core_cycle.speak_current_question()
        self.finished_signal.emit()

    def stop(self):
        self._running = False
        if hasattr(self.core_cycle, 'audio_player') and self.core_cycle.audio_player:
            self.core_cycle.audio_player.stop()

        # Ek ses durdurma işlemleri

        TextToSpeech.tts_durdur()

        try:
            import sounddevice as sd
            sd.stop()
        except:
            pass


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PREVENTRAL Aday Paneli (UI)")
    app.setApplicationVersion("1.0.0")
    window = AdayPanelApp()
    window.show()
    screen = app.desktop().screenGeometry()
    size = window.geometry()
    window.move(int((screen.width() - size.width()) / 2),
                int((screen.height() - size.height()) / 2))
    sys.exit(app.exec_())


main()
