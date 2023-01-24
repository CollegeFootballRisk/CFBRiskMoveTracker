import sys
from datetime import datetime


class Logger:
    def __init__(self, log_path="script.log"):
        self.log_path = log_path

    def log(self, message):
        sys.stdin.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')
        log_line = f"{datetime.utcnow().isoformat()} {message}"
        print(log_line)
        with open(self.log_path, "a", encoding='utf-8') as file:
            file.write(log_line + '\n')
