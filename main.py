import argparse
import json
import unittest

from discord_api import DiscordApi
from logger import Logger
from risk_api import RiskApi, MockRiskApi


class Main:
    def __init__(self):
        self.risk_api = RiskApi()
        self.csv_suffix = "Stars.csv"
        self.discord_api = DiscordApi()
        self.username_map_file = "username_map.json"
        self.stars = {}
        self.star_char = "⭐"  # ⭐ ✯ * 🌟 ☆

    def cache_all_stars(self):
        if self.stars == {}:
            self.stars.update(self.risk_api.get_player_stars(self.risk_api.get_players()))
            self.stars.update(self.risk_api.get_merc_stars(self.risk_api.get_mercs()))

    def generate_csv(self):
        self.cache_all_stars()
        csv = "Reddit Name,Stars,Last Day Played\n"
        for player in self.stars:
            player_info = self.risk_api.get_player_info(player)
            last_day_played = 0
            player_turns = player_info["turns"]
            if len(player_turns) > 0:
                last_day_played = player_turns[0]["day"]
            csv += f"{player},{self.stars[player]},{last_day_played}\n"
        return csv

    def write_csv_file(self):
        Logger.log("Writing CSV file...")
        day_number = self.risk_api.get_previous_turn()['day']
        csv_name = f"Day {day_number} {self.csv_suffix}"
        with open(csv_name, "w") as file:
            file.write(self.generate_csv())
        Logger.log("Done writing CSV file.")

    def get_username_mapping(self):
        with open(self.username_map_file, 'r') as file:
            return json.load(file)

    def build_discord_nickname(self, mapping):
        self.cache_all_stars()
        reddit_username = mapping['reddit']
        if reddit_username not in self.stars:
            Logger.log(f"Error: Reddit username \"{reddit_username}\" is not in the star list.")
        nickname = f"{reddit_username} {self.star_char * self.stars[reddit_username]}"  # "[prefix|]username ✯✯✯✯✯"
        if "prefix" in mapping:
            nickname = f"{mapping['prefix']} | {nickname}"
        return nickname

    def set_discord_nicknames(self):
        Logger.log("Setting Discord nicknames...")
        discord_ids = self.discord_api.get_guild_member_ids()
        mapping = self.get_username_mapping()
        for discord_id in discord_ids:
            if discord_id in mapping["exclude"] or discord_id == self.discord_api.get_bot_id():
                continue
            elif discord_id in mapping["map"]:
                nickname = self.build_discord_nickname(mapping["map"][discord_id])
                if len(nickname) > 32:
                    Logger.log(f"Warning: Nickname \"{nickname}\" is >32 characters. Skipping.")
                    continue
                self.discord_api.set_nickname(discord_id, nickname)
            else:
                user = self.discord_api.get_guild_member(discord_id)
                Logger.log(f"Warning: Discord ID {discord_id} (nick=\"{user['nick']}\") is not in the map file.")
        Logger.log("Done setting Discord nicknames.")

    def test_set_discord_nickname(self):
        self.discord_api.use_test_guild()
        self.discord_api.set_nickname(self.discord_api.secrets["test_user_id"], f"test|EpicWolverine {self.star_char * 4}")


class TestSuite(unittest.TestCase):
    def setUp(self) -> None:
        self.cut = Main()
        self.cut.risk_api = MockRiskApi()

    def test_csv_generation(self):
        expected = "Reddit Name,Stars,Last Day Played\nuser1,4,18\nEpicWolverine,4,18\nuser2,4,0\nmerc1,4,18\nMautamu,3,16\n"
        self.assertEqual(self.cut.generate_csv(), expected)


if __name__ == "__main__":
    Logger.log("Script start.")
    main = Main()
    parser = argparse.ArgumentParser(description="Automate logging and setting Risk Stars. Default: Generate stars CSV and update Discord nicknames.")
    parser.add_argument("-auth", "--authenticate", action="store_const",
                        const=True, default=False,
                        help="Only open bot authentication link.")
    parser.add_argument("-nick", "--nickname", action="store_const", const=True, default=False,
                        help="Only update Discord nicknames.")
    parser.add_argument("-test_nick", "--test_nickname", action="store_const", const=True, default=False,
                        help="Only test Discord nickname updating.")
    parser.add_argument("-prod", "--use_prod_guild", action="store_const", const=True, default=False,
                        help="Use production guild.")
    args = parser.parse_args()
    if not args.use_prod_guild:
        main.discord_api.use_test_guild()
        main.username_map_file = "test_username_map.json"
    if args.authenticate:
        main.discord_api.launch_bot_auth()
    elif args.test_nickname:
        main.test_set_discord_nickname()
    else:
        if not args.nickname:
            main.write_csv_file()
        main.set_discord_nicknames()
    Logger.log("Script end.")
