import argparse
import json
import unittest

from discord_api import DiscordApi
from logger import Logger
from risk_api import RiskApi, MockRiskApi

NICKNAME_CHAR_LIMIT = 32


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
            self.risk_api.get_batch_player_info(self.risk_api.get_players())
            self.risk_api.get_batch_player_info(self.risk_api.get_mercs())
            self.stars.update(self.risk_api.get_player_stars(self.risk_api.get_players()))
            self.stars.update(self.risk_api.get_merc_stars(self.risk_api.get_mercs()))

    def generate_csv(self):
        self.cache_all_stars()
        csv = "Reddit Name,Original Team,Overall Stars,Last Turn Played,Last Turn Territory," \
              "Total Turns,Total Turns Stars,Game Turns,Game Turns Stars,MVPs,MVP Stars,Streak,Streak Stars\n"
        for player in self.stars:
            player_info = self.risk_api.get_player_info(player)
            player_turns = player_info["turns"]
            last_turn = player_turns[0] if len(player_turns) > 0 else {"season": "", "day": "", "territory": ""}
            csv += f"{player},{player_info['team']['name']},{self.stars[player]}," \
                   f"{last_turn['season']}/{last_turn['day']},{last_turn['territory']}," \
                   f"{player_info['stats']['totalTurns']},{player_info['ratings']['totalTurns']}," \
                   f"{player_info['stats']['gameTurns']},{player_info['ratings']['gameTurns']}," \
                   f"{player_info['stats']['mvps']},{player_info['ratings']['mvps']}," \
                   f"{player_info['stats']['streak']},{player_info['ratings']['streak']}\n"
        return csv

    def write_csv_file(self):
        Logger.log("Writing CSV file...")
        previous_turn = self.risk_api.get_previous_turn()
        csv_name = f"Season {previous_turn['season']} Day {previous_turn['day']} {self.csv_suffix}"
        with open(csv_name, "w") as file:
            file.write(self.generate_csv())
        Logger.log("Done writing CSV file.")

    def get_username_mapping(self):
        with open(self.username_map_file, 'r') as file:
            return json.load(file)

    def build_discord_nickname_with_stars(self, mapping):
        self.cache_all_stars()
        reddit_username = mapping['reddit']
        if reddit_username not in self.stars:
            Logger.log(f"Error: Reddit username \"{reddit_username}\" is not in the star list.")
            return None
        nickname = f"{reddit_username} {self.star_char * self.stars[reddit_username]}"  # "[prefix|]username ✯✯✯✯✯"
        if "prefix" in mapping:
            prefixed_nickname = f"{mapping['prefix']} | {nickname}"
            if len(prefixed_nickname) <= NICKNAME_CHAR_LIMIT:
                nickname = prefixed_nickname
            else:
                Logger.log(f"Warning: Prefixed nickname \"{prefixed_nickname}\" is >{NICKNAME_CHAR_LIMIT} characters. Ignoring prefix.")
        return nickname

    def set_discord_nickname(self, discord_id: str, nickname: str) -> None:
        if len(nickname) > NICKNAME_CHAR_LIMIT:
            Logger.log(f"Warning: Nickname \"{nickname}\" is >{NICKNAME_CHAR_LIMIT} characters. Skipping.")
            return
        self.discord_api.set_nickname(discord_id, nickname)

    def set_discord_nicknames(self):
        Logger.log("Setting Discord nicknames...")
        discord_ids = self.discord_api.get_guild_member_ids()
        mapping = self.get_username_mapping()
        for discord_id in discord_ids:
            if discord_id in mapping["exclude"] or discord_id == self.discord_api.get_bot_id():
                continue
            elif discord_id in mapping["players"]:
                nickname = self.build_discord_nickname_with_stars(mapping["players"][discord_id])
                if nickname is None:
                    continue
                self.set_discord_nickname(discord_id, nickname)
            elif discord_id in mapping["diplomats"]:
                diplomat = mapping["diplomats"][discord_id]
                self.set_discord_nickname(discord_id, f"{diplomat['nickname']} | {diplomat['team']}")
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
        self.assertEqual(expected, self.cut.generate_csv())


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
