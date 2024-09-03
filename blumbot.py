import sys
import time
import random
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import pygetwindow as gw
import pyautogui
import keyboard
from pynput.mouse import Button as MouseButton, Controller
import cv2
import numpy as np

# Initialize mouse controller
mouse = Controller()

class AutomationApp(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_language = None
        self.paused = False
        self.bot_thread = None
        self.bot_running = False

        self.initUI()

    def initUI(self):
        # Window settings
        self.setWindowTitle("Blum Automation Clicker")
        self.setGeometry(100, 100, 500, 500)
        self.setFixedSize(500, 500)

        # Apply modern stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #444444;
                border: none;
                color: white;
                padding: 12px;
                font-size: 14px;
                border-radius: 8px;
                min-width: 140px;
                margin: 5px;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #aaaaaa;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QLabel {
                font-size: 16px;
                padding: 5px;
            }
        """)

        # UI Elements
        self.language_label = QLabel("...:::: CHOOSE LANGUAGE ::::...", self)
        self.language_label.setFont(QFont("Helvetica", 16))
        self.language_label.setAlignment(Qt.AlignCenter)

        self.english_button = QPushButton(QIcon('icons/english.png'), "English", self)
        self.english_button.setFont(QFont("Helvetica", 14))
        self.english_button.clicked.connect(lambda: self.choose_language(1))

        self.bahasa_button = QPushButton(QIcon('icons/bahasa.png'), "Bahasa Indonesia", self)
        self.bahasa_button.setFont(QFont("Helvetica", 14))
        self.bahasa_button.clicked.connect(lambda: self.choose_language(2))

        self.test_label = QLabel("Blum AutoClicker", self)
        self.test_label.setFont(QFont("Helvetica", 14))
        self.test_label.setAlignment(Qt.AlignCenter)

        self.author_label = QLabel("Author: Lavize", self)
        self.author_label.setFont(QFont("Helvetica", 12))
        self.author_label.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton(QIcon('icons/start.png'), "Start Automation", self)
        self.start_button.setFont(QFont("Helvetica", 14))
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_automation)

        self.exit_button = QPushButton(QIcon('icons/exit.png'), "Exit", self)
        self.exit_button.setFont(QFont("Helvetica", 14))
        self.exit_button.clicked.connect(self.exit_program)

        self.status_label = QLabel("Bot Status: Not Started", self)
        self.status_label.setFont(QFont("Helvetica", 12))
        self.status_label.setAlignment(Qt.AlignCenter)

        self.instruction_label = QLabel("Press 'K' to Play/Pause", self)
        self.instruction_label.setFont(QFont("Helvetica", 12))
        self.instruction_label.setAlignment(Qt.AlignCenter)

        # Layout
        main_layout = QVBoxLayout()

        main_layout.addWidget(self.test_label)
        main_layout.addWidget(self.language_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.english_button)
        button_layout.addWidget(self.bahasa_button)
        main_layout.addLayout(button_layout)

        main_layout.addWidget(self.author_label)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.start_button)
        action_layout.addWidget(self.exit_button)
        main_layout.addLayout(action_layout)

        main_layout.addWidget(self.instruction_label)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def choose_language(self, choice):
        self.selected_language = choice
        self.start_button.setEnabled(True)
        
        # Change button text based on language selection
        if choice == 1:  # English
            self.language_label.setText("...:::: CHOOSE LANGUAGE ::::...")
            self.start_button.setText("Start Automation")
            self.exit_button.setText("Exit")
            self.english_button.setText("English")
            self.bahasa_button.setText("Bahasa Indonesia")
            QMessageBox.information(self, "Language Selected", "Language selected. Click 'Start Automation' to proceed.")
        else:  # Bahasa Indonesia
            self.language_label.setText("...:::: PILIH BAHASA ::::...")
            self.start_button.setText("Mulai Otomatisasi")
            self.exit_button.setText("Keluar")
            self.english_button.setText("Bahasa Inggris")
            self.bahasa_button.setText("Bahasa Indonesia")
            QMessageBox.information(self, "Bahasa Dipilih", "Bahasa telah dipilih. Klik 'Mulai Otomatisasi' untuk melanjutkan.")

    def get_language_messages(self, language_choice):
        if language_choice == 1:
            return {
                "window_input": "Enter Window (1 - TelegramDesktop): ",
                "window_not_found": "Your Window - {} not found!\nOpen Blum app in Telegram.",
                "window_found": "Window found - {}\nNow bot working... Press 'K' on the keyboard to pause.",
                "pause_message": "Bot paused... Press 'K' again on the keyboard to continue.",
                "continue_message": "Bot continue working...",
                "instructions": "Make sure TelegramDesktop is open and visible on your screen before proceeding."
            }
        else:
            return {
                "window_input": "Masukin Window nya (1 - TelegramDesktop): ",
                "window_not_found": "Window - {} gak di temukan!\nBuka Blum app di Telegram.",
                "window_found": "Window ditemukan - {}\nSekarang bot berjalan... Pencet 'K' di keyboard buat jeda.",
                "pause_message": "Bot terjeda... Pencet 'K' di keyboard buat lanjut lagi.",
                "continue_message": "Bot ngelanjutin proses...",
                "instructions": "Pastikan TelegramDesktop terbuka dan terlihat di layar sebelum melanjutkan."
            }

    def get_telegram_window(self, messages):
        while True:
            window_name = "TelegramDesktop"
            check = gw.getWindowsWithTitle(window_name)
            if not check:
                QMessageBox.warning(self, "Window Not Found", messages["window_not_found"].format(window_name))
                return None
            else:
                QMessageBox.information(self, "Window Found", messages["window_found"].format(window_name))
                return check[0]

    def start_automation(self):
        if self.selected_language is None:
            QMessageBox.warning(self, "No Language Selected", "Please select a language before starting.")
            return

        messages = self.get_language_messages(self.selected_language)
        telegram_window = self.get_telegram_window(messages)

        if not telegram_window:
            return

        self.bot_running = True
        self.bot_thread = threading.Thread(target=self.run_bot, args=(telegram_window, messages))
        self.bot_thread.start()

    def run_bot(self, telegram_window, messages):
        self.update_status("Bot Status: Running")
        self.paused = False

        while self.bot_running:
            if keyboard.is_pressed('K'):
                self.paused = not self.paused
                self.update_status("Bot Status: Paused" if self.paused else "Bot Status: Running")
                time.sleep(0.2)

            if self.paused:
                continue

            try:
                telegram_window.activate()
            except:
                telegram_window.minimize()
                telegram_window.restore()

            window_rect = (
                telegram_window.left, telegram_window.top, telegram_window.width, telegram_window.height
            )
            scrn = pyautogui.screenshot(region=window_rect)

            # Convert screenshot to numpy array (compatible with OpenCV)
            scrn_np = np.array(scrn)
            scrn_np = cv2.cvtColor(scrn_np, cv2.COLOR_RGB2BGR)

            # Text detection with template matching
            text_found = self.detect_text(scrn_np, window_rect)
            if text_found:
                continue  # If text "play" is detected and clicked, skip color detection

            # Color detection
            self.detect_color(scrn, window_rect)

    def detect_text(self, scrn_np, window_rect):
        # Load the template image (this should be an image of the word "play")
        template = cv2.imread('play_template.png', 0)

        # Convert the screenshot to grayscale
        gray_scrn = cv2.cvtColor(scrn_np, cv2.COLOR_BGR2GRAY)

        # Apply template matching
        result = cv2.matchTemplate(gray_scrn, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Define a threshold to decide if the template is found
        threshold = 0.8
        if max_val >= threshold:
            template_w, template_h = template.shape[::-1]

            # Calculate the center of the detected area to click
            center_x = window_rect[0] + max_loc[0] + template_w // 2
            center_y = window_rect[1] + max_loc[1] + template_h // 2

            # Perform a click at the center of the detected word "play"
            self.click(center_x, center_y)
            return True  # Stop further processing once 'play' is found and clicked

        return False

    def detect_color(self, scrn, window_rect):
        width, height = scrn.size
        pixel_found = False

        for x in range(0, width, 20):
            for y in range(0, height, 20):
                r, g, b = scrn.getpixel((x, y))
                if (b in range(0, 125)) and (r in range(102, 220)) and (g in range(200, 255)):
                    screen_x = window_rect[0] + x
                    screen_y = window_rect[1] + y
                    self.click(screen_x + 4, screen_y)
                    pixel_found = True
                    break
            if pixel_found:
                break

    def click(self, x, y):
        # Introduce slight randomness to the click position to avoid detection as a bot
        jitter_x = random.randint(-2, 2)
        jitter_y = random.randint(-2, 2)
        mouse.position = (x + jitter_x, y + jitter_y)
        mouse.press(MouseButton.left)
        mouse.release(MouseButton.left)

    def update_status(self, status):
        self.status_label.setText(status)

    def exit_program(self):
        self.bot_running = False
        if self.bot_thread:
            self.bot_thread.join()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AutomationApp()
    ex.show()
    sys.exit(app.exec_())
