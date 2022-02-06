import json
import re
import requests
import webbrowser
import sys


class DiscordApi:
    def __init__(self):
        self.api_endpoint = 'https://discord.com/api/v8'
        with open("secrets.json") as f:
            self.secrets = json.load(f)

    def launch_bot_auth(self):
        webbrowser.open(f"{self.api_endpoint}/oauth2/authorize?client_id={self.secrets['client_id']}&scope=bot&permissions=134217728&guild_id={self.secrets['guild_id']}&disable_guild_select=true")

    def get_guild_members(self):
        params = {"limit": 1000}
        headers = {"Authorization": f"Bot {self.secrets['bot_token']}"}
        r = requests.get(f"{self.api_endpoint}/guilds/{self.secrets['guild_id']}/members", params=params, headers=headers)
        r.raise_for_status()
        return r.json()

    def get_guild_member_names(self):
        api_list = self.get_guild_members()
        names = {}
        for guild_member in api_list:
            discord_username = f"{guild_member['user']['username']}#{guild_member['user']['discriminator']}"
            server_nickname = guild_member['nick']
            names[discord_username] = server_nickname
        return names

    def parse_nickname(self, nickname):
        stars_chars = ['⭐', '✯', '*', '🌟', '☆']
        stars = re.search(r"[⭐✯*🌟☆]+", nickname).group()
        reddit_username = re.search(r"u/([\w-]+)", nickname).group(1)


if __name__ == "__main__":
    api = DiscordApi()
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        api.launch_bot_auth()
    else:
        print(api.get_guild_members())
