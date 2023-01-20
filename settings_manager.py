import json


class SettingsManager:
    def __init__(self):
        with open("settings.json") as f:
            self.settings = json.load(f)
