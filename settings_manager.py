import json

SETTINGS_FILE_NAME = "settings.json"


class SettingsManager:
    def __init__(self):
        with open(SETTINGS_FILE_NAME) as f:
            self.settings = json.load(f)

    def get_secrets(self):
        secrets = self.settings.get("secrets")
        if secrets is None:
            raise KeyError(f'"secrets" and its child keys must be defined in {SETTINGS_FILE_NAME}')
        return secrets

    def get_team_name(self):
        team = self.settings.get("settings").get("team")
        if team is None:
            raise KeyError(f'"settings.team" must be defined in {SETTINGS_FILE_NAME}')
        return team

    def get_verified_discord_role_name(self):
        return self.settings.get("settings").get("verified_discord_role_name")
