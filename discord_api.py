import requests
import time
import webbrowser
import sys

from logger import Logger
from settings_manager import SettingsManager


class DiscordCache:
    def __init__(self):
        self.guild_members = None
        self.bot_id = None
        self.guild_roles = None


class DiscordApi:
    def __init__(self):
        self.api_base_url = 'https://discord.com/api/v9'
        self.secrets = SettingsManager().get_secrets()
        self.headers = {"Authorization": f"Bot {self.secrets['bot_token']}"}
        self.cache = DiscordCache()
        self.logger = Logger()

    def launch_bot_auth(self):
        webbrowser.open(f"{self.api_base_url}/oauth2/authorize?client_id={self.secrets['client_id']}&scope=bot&permissions=134217728&guild_id={self.secrets['guild_id']}&disable_guild_select=true")

    def call_api_get(self, endpoint, params=None) -> dict:
        url = f"{self.api_base_url}/{endpoint}"
        self.logger.log(f"Calling GET {url}")
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
        if self.cache.bot_id is None:
            self.cache.bot_id = self.call_api_get(f"users/@me")['id']
        return self.cache.bot_id

    def get_guild_member(self, discord_id):
        cached_member = next((item for item in self.cache.guild_members if item["user"]["id"] == discord_id), None)
        if cached_member is None and discord_id:
            cached_member = self.call_api_get(f"guilds/{self.secrets['guild_id']}/members/{discord_id}")
            if "user" in cached_member:
                self.cache.guild_members.append(cached_member)
            else:
                return
        return cached_member

    def get_guild_members(self):
        if self.cache.guild_members is None:
            params = {"limit": 1000}
            self.cache.guild_members = self.call_api_get(f"guilds/{self.secrets['guild_id']}/members", params=params)
        return self.cache.guild_members

    def get_guild_member_ids(self) -> list[str]:
        return [guild_member['user']['id'] for guild_member in self.get_guild_members()]

    def get_guild_roles(self) -> list[dict]:
        if self.cache.guild_roles is None:
            self.cache.guild_roles = self.call_api_get(f"guilds/{self.secrets['guild_id']}/roles")
        return self.cache.guild_roles

    def call_api_patch(self, endpoint, body) -> dict:
        url = f"{self.api_base_url}/{endpoint}"
        self.logger.log(f"Calling PATCH {url}")
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
        url = f"guilds/{self.secrets['guild_id']}/members/{discord_id}"
        body = {"nick": nickname}
        return self.call_api_patch(url, body)

    def use_test_guild(self):
        self.secrets["guild_id"] = self.secrets["test_guild_id"]


if __name__ == "__main__":
    logger = Logger()
    api = DiscordApi()
    api.use_test_guild()
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        api.launch_bot_auth()
    else:
        logger.log(api.get_guild_members())
        logger.log(api.get_bot_id())
