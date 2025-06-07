from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QSpinBox
)
from bot import JobBot
import sys
import threading

bot = None

def start_ui():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("CrowdWorks Discord Bot")

    layout = QVBoxLayout()

    webhook_label = QLabel("Discord Webhook URL:")
    webhook_input = QLineEdit("https://discord.com/api/webhooks/1380639610220187699/v35fb8y1WA9Woxn55x2PgaXxh-4beew3t4VqorFvTAfCYVgHKn2HlT0Oqp__sZ4VqSLt")
    layout.addWidget(webhook_label)
    layout.addWidget(webhook_input)

    url_label = QLabel("CrowdWorks Job URL:")
    url_input = QLineEdit("https://crowdworks.jp/public/jobs/group/development")
    layout.addWidget(url_label)
    layout.addWidget(url_input)

    keyword_label = QLabel("Keywords (comma-separated):")
    keyword_input = QLineEdit()
    layout.addWidget(keyword_label)
    layout.addWidget(keyword_input)

    interval_label = QLabel("Update Interval (seconds):")
    interval_input = QSpinBox()
    interval_input.setMinimum(10)
    interval_input.setMaximum(3600)
    interval_input.setValue(10)
    layout.addWidget(interval_label)
    layout.addWidget(interval_input)

    log_output = QTextEdit()
    log_output.setReadOnly(True)
    layout.addWidget(log_output)

    def start_bot():
        global bot
        log_output.append("🟢 Bot started!")
        keywords = [kw.strip().lower() for kw in keyword_input.text().split(',') if kw.strip()]
        bot = JobBot(
            webhook_input.text(),
            url_input.text(),
            keywords,
            interval_input.value(),
            log_output
        )
        webhook_input.setDisabled(True)
        url_input.setDisabled(True)
        keyword_input.setDisabled(True)
        interval_input.setDisabled(True)
        start_btn.setDisabled(True)
        stop_btn.setDisabled(False)
        threading.Thread(target=bot.run, daemon=True).start()

    def stop_bot():
        global bot
        if bot:
            bot.running = False
            log_output.append("🔴Bot stopped.")
            webhook_input.setDisabled(False)
            url_input.setDisabled(False)
            keyword_input.setDisabled(False)
            interval_input.setDisabled(False)
            start_btn.setDisabled(False)
            stop_btn.setDisabled(True)

    start_btn = QPushButton("Start Bot")
    start_btn.clicked.connect(start_bot)
    layout.addWidget(start_btn)

    stop_btn = QPushButton("Stop Bot")
    stop_btn.clicked.connect(stop_bot)
    layout.addWidget(stop_btn)

    window.setLayout(layout)
    window.resize(500, 500)
    window.show()
    sys.exit(app.exec_())
