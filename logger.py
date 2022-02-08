import sys
from datetime import datetime


class Logger:
    @staticmethod
    def log(message):
        sys.stdin.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')
        log_line = f"{datetime.utcnow().isoformat()} {message}"
        print(log_line)
        with open("script.log", "a", encoding='utf-8') as file:
            file.write(log_line + '\n')
