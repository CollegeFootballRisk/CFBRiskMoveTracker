import json
import requests
import webbrowser
import sys


class DiscordApi:
    def __init__(self):
        self.api_endpoint = 'https://discord.com/api/v9'
        with open("secrets.json") as f:
            self.secrets = json.load(f)
        self.headers = {"Authorization": f"Bot {self.secrets['bot_token']}"}

    def launch_bot_auth(self):
        webbrowser.open(f"{self.api_endpoint}/oauth2/authorize?client_id={self.secrets['client_id']}&scope=bot&permissions=134217728&guild_id={self.secrets['guild_id']}&disable_guild_select=true")

    def get_guild_members(self):
        params = {"limit": 1000}
        r = requests.get(f"{self.api_endpoint}/guilds/{self.secrets['guild_id']}/members", params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def get_guild_member_ids(self):
        ids = []
        for guild_member in self.get_guild_members():
            ids.append(guild_member['user']['id'])
        return ids

    def set_nickname(self, discord_id, nickname):
        print(f"Setting {discord_id} to {nickname}")
        body = {"nick": nickname}
        r = requests.patch(f"{self.api_endpoint}/guilds/{self.secrets['guild_id']}/members/{discord_id}", json=body, headers=self.headers)
        print(r.json())
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":
    api = DiscordApi()
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        api.launch_bot_auth()
    else:
        print(api.get_guild_members())
