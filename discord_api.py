import requests
import time
import webbrowser
import sys

from logger import Logger
from settings_manager import SettingsManager


class DiscordApi:
    def __init__(self):
        self.api_endpoint = 'https://discord.com/api/v9'
        self.secrets = SettingsManager().get_secrets()
        self.headers = {"Authorization": f"Bot {self.secrets['bot_token']}"}
        self.bot_id = None
        self.logger = Logger()

    def launch_bot_auth(self):
        webbrowser.open(f"{self.api_endpoint}/oauth2/authorize?client_id={self.secrets['client_id']}&scope=bot&permissions=134217728&guild_id={self.secrets['guild_id']}&disable_guild_select=true")

    def call_api_get(self, url, params=None) -> dict:
        r = requests.get(url, params=params, headers=self.headers)
        response = r.json()
        try:
            r.raise_for_status()
        except Exception as e:
            self.logger.log(response)
            self.logger.log(e)
            if "retry_after" in response:
                delay = response["retry_after"]
                self.logger.log(f"Waiting {delay} seconds.")
                time.sleep(delay)
                response = self.call_api_get(url, params)
        return response

    def get_bot_id(self):
        if self.bot_id is None:
            self.bot_id = self.call_api_get(f"{self.api_endpoint}/users/@me")['id']
        return self.bot_id

    def get_guild_member(self, discord_id):
        return self.call_api_get(f"{self.api_endpoint}/guilds/{self.secrets['guild_id']}/members/{discord_id}")

    def get_guild_members(self):
        params = {"limit": 1000}
        return self.call_api_get(f"{self.api_endpoint}/guilds/{self.secrets['guild_id']}/members", params=params)

    def get_guild_member_ids(self):
        ids = []
        for guild_member in self.get_guild_members():
            ids.append(guild_member['user']['id'])
        return ids

    def call_api_patch(self, url, body) -> dict:
        r = requests.patch(url, json=body, headers=self.headers)
        response = r.json()
        try:
            r.raise_for_status()
        except Exception as e:
            self.logger.log(response)
            self.logger.log(e)
            if "retry_after" in response:
                delay = response["retry_after"]
                self.logger.log(f"Waiting {delay} seconds.")
                time.sleep(delay)
                response = self.call_api_patch(url, body)
        return response

    def set_nickname(self, discord_id, nickname):
        self.logger.log(f"Setting {discord_id} to \"{nickname}\"")
        url = f"{self.api_endpoint}/guilds/{self.secrets['guild_id']}/members/{discord_id}"
        body = {"nick": nickname}
        return self.call_api_patch(url, body)

    def use_test_guild(self):
        self.secrets["guild_id"] = self.secrets["test_guild_id"]


if __name__ == "__main__":
    api = DiscordApi()
    api.use_test_guild()
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        api.launch_bot_auth()
    else:
        self.logger.log(api.get_guild_members())
        self.logger.log(api.get_bot_id())
