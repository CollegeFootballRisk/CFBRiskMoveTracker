import json
import requests
import unittest

from logger import Logger
from settings_manager import SettingsManager

MAX_BATCH_SIZE = 400


class RiskApiCache:
    def __init__(self):
        self.players = None
        self.mercs = None
        self.player_info = {}
        self.turns = None
        self.territory_turn = {}


class RiskApi:
    def __init__(self):
        self.api_base_url = "https://collegefootballrisk.com/api"
        self.cache = RiskApiCache()
        self.team = SettingsManager().get_team_name()
        self.logger = Logger()

    def _call_api(self, endpoint, params=None):
        api_url = f"{self.api_base_url}/{endpoint}"
        self.logger.log(f"Calling GET {api_url} {params=}")
        headers = {"Content-Type": "application/json"}
        return requests.get(api_url, headers=headers, params=params).json()

    def _get_team_api_data(self, endpoint):
        return self._call_api(endpoint, {"team": self.team})

    def get_players(self):
        if self.cache.players is None:
            self.cache.players = self._get_team_api_data("players")
        return self.cache.players

    def get_mercs(self):
        if self.cache.mercs is None:
            self.cache.mercs = self._get_team_api_data("mercs")
        return self.cache.mercs

    def get_player_stars(self, player_names: list):
        player_stars = {}
        for player_name in player_names:
            player_stars[player_name] = self.get_player_info(player_name)["ratings"]["overall"]
        return player_stars

    def get_merc_stars(self, mercs: list[dict]):
        merc_stars = {}
        for merc in mercs:
            merc_stars[merc["player"]] = merc["stars"]
        return merc_stars

    def _get_player_api_data(self, player_name):
        return self._call_api("player", {"player": player_name})

    def get_player_info(self, player_name):
        if player_name not in self.cache.player_info or self.cache.player_info[player_name] is None:
            self.cache.player_info[player_name] = self._get_player_api_data(player_name)
        return self.cache.player_info[player_name]

    def _get_batch_player_api_data(self, player_names):
        if player_names:
            players_data = []
            for i in range(0, len(player_names), MAX_BATCH_SIZE):
                players_data += self._call_api("players/batch", {"players": ','.join(player_names[i:i + MAX_BATCH_SIZE])})
            return players_data
        return []

    def get_batch_player_info(self, player_names: list) -> list[dict]:
        players_info = self._get_batch_player_api_data(player_names)
        for player in players_info:
            self.cache.player_info[player["name"]] = player
        return players_info

    def _get_turns_api_data(self) -> list[dict]:
        return self._call_api(f"turns")

    def get_turns(self) -> list[dict]:
        if self.cache.turns is None:
            self.cache.turns = self._get_turns_api_data()
            self.cache.turns.sort(key=lambda turn: turn["id"])
        return self.cache.turns

    def get_previous_turn(self) -> dict:
        return self.get_turns()[-2]

    def _get_territory_turn_api_data(self, season: int, day: int, territory: str) -> dict:
        return self._call_api("territory/turn", {"season": season, "day": day, "territory": territory})

    def get_territory_turn(self, season: int, day: int, territory: str) -> dict:
        if season not in self.cache.territory_turn:
            self.cache.territory_turn[season] = {}
        if day not in self.cache.territory_turn[season]:
            self.cache.territory_turn[season][day] = {}
        if territory not in self.cache.territory_turn[season][day]:
            self.cache.territory_turn[season][day][territory] = self._get_territory_turn_api_data(season, day, territory)
        return self.cache.territory_turn[season][day][territory]


class MockRiskApi(RiskApi):
    def __init__(self):
        super().__init__()
        self._get_team_api_data_access_count = {"players": 0, "mercs": 0}
        self._get_player_api_data_access_count = 0

    def _get_team_api_data(self, endpoint):
        self._get_team_api_data_access_count[endpoint] += 1
        if endpoint == "players":
            return json.loads('[{"team": "Aldi", "player": "user1", "turnsPlayed": 16, "mvps": 6, "lastTurn": {"season": 1, "day": 17, "stars": 3}}, {"team": "Aldi", "player": "EpicWolverine", "turnsPlayed": 112, "mvps": 9, "lastTurn": {"season": 1, "day": 17, "stars": 4}}, {"team": "Aldi","player": "user2","turnsPlayed": 92,"mvps": 12,"lastTurn": {"season": -1,"day": 116,"stars": 4}}]')
        elif endpoint == "mercs":
            return json.loads('[{"team": "Aldi", "player": "merc1", "turnsPlayed": 67, "mvps": 6, "stars": 4}, {"team": "Aldi", "player": "Mautamu", "turnsPlayed": 57, "mvps": 6, "stars": 3}]')
        else:
            return super()._get_team_api_data(endpoint)

    def _get_player_api_data(self, player_name):
        self._get_player_api_data_access_count += 1
        if player_name == "EpicWolverine":
            return json.loads('{"active_team": {"name": "Aldi"},"name": "EpicWolverine","platform": "reddit","ratings": {"awards": 5,"gameTurns": 3,"mvps": 4,"overall": 4,"streak": 4,"totalTurns": 5},"stats": {"awards": 5,"gameTurns": 18,"mvps": 10,"streak": 18,"totalTurns": 113},"team": {"name": "Aldi"},"turns": [{"day": 18,"mvp": true,"season": 1,"stars": 4,"team": "Aldi","territory": "Alaska"},{"day": 17,"mvp": false,"season": 1,"stars": 4,"team": "Aldi","territory": "Minnesota"}]}')
        elif player_name == "user1":
            return json.loads('{"name": "user1","ratings": {"awards": 5,"gameTurns": 3,"mvps": 4,"overall": 4,"streak": 4,"totalTurns": 5},"stats": {"awards": 5,"gameTurns": 18,"mvps": 10,"streak": 18,"totalTurns": 113},"turns": [{"day": 18,"mvp": true,"season": 1,"stars": 4,"team": "Aldi","territory": "Alaska"}]}')
        elif player_name == "user2":
            return json.loads('{"name": "user2","ratings": {"overall": 4,"totalTurns": 4,"gameTurns": 1,"mvps": 4,"streak": 1,"awards": 5},"stats": {"totalTurns": 92,"gameTurns": 0,"mvps": 12,"streak": 0,"awards": 5},"turns": []}')
        elif player_name == "merc1":
            return json.loads('{"name": "merc1","ratings": {"awards": 5,"gameTurns": 3,"mvps": 4,"overall": 4,"streak": 4,"totalTurns": 5},"stats": {"awards": 5,"gameTurns": 18,"mvps": 10,"streak": 18,"totalTurns": 113},"turns": [{"day": 18,"mvp": true,"season": 1,"stars": 4,"team": "Aldi","territory": "Alaska"}]}')
        elif player_name == "Mautamu":
            return json.loads('{"name": "Mautamu","ratings": {"awards": 5,"gameTurns": 3,"mvps": 3,"overall": 3,"streak": 3,"totalTurns": 5},"stats": {"awards": 5,"gameTurns": 18,"mvps": 10,"streak": 18,"totalTurns": 113},"turns": [{"day": 16,"mvp": true,"season": 1,"stars": 3,"team": "Aldi","territory": "Alaska"}]}')

    def _get_batch_player_api_data(self, player_names):
        return json.loads('[{"name": "EpicWolverine", "platform": "reddit", "ratings": {"awards": 5, "gameTurns": 3, "mvps": 4, "overall": 4, "streak": 4, "totalTurns": 5}, "stats": {"awards": 5, "gameTurns": 18, "mvps": 10, "streak": 18, "totalTurns": 113}, "team": {"name": "Aldi"}, "turns": [{"day": 18, "mvp": true, "season": 1, "stars": 4, "team": "Aldi", "territory": "Alaska"}, {"day": 17, "mvp": false, "season": 1, "stars": 4, "team": "Aldi", "territory": "Minnesota"}]}, {"name": "Mautamu", "team": {"name": "Texas A&M"}, "platform": "reddit", "ratings": {"overall": 1, "totalTurns": 3, "gameTurns": 1, "mvps": 1, "streak": 1}, "stats": {"totalTurns": 42, "gameTurns": 0, "mvps": 0, "streak": 0}, "turns": [{"season": 2, "day": 50, "stars": 3, "mvp": false, "territory": "Stillwater", "team": "Texas A&M"}]} ]')

    def _get_turns_api_data(self):
        return [
            {"id": 20, "season": 1, "day": 20, "complete": False, "active": True, "finale": False, "rollTime": None},
            {"id": 19, "season": 1, "day": 19, "complete": True, "active": False, "finale": False, "rollTime": "2022-02-06T03:30:01.685073"},
            {"id": 18, "season": 1, "day": 18, "complete": True, "active": False, "finale": False, "rollTime": "2022-02-05T03:30:01.032336"},
            {"id": 17, "season": 1, "day": 17, "complete": True, "active": False, "finale": False, "rollTime": "2022-02-04T03:30:01.032336"}
        ]


class TestSuite(unittest.TestCase):
    def setUp(self) -> None:
        self.cut = MockRiskApi()

    def test_get_players(self):
        self.assertIsNotNone(self.cut.get_players())
        self.assertIsNotNone(self.cut.get_mercs())

    def test_stars(self):
        self.assertEqual({"user1": 4, "EpicWolverine": 4, "user2": 4}, self.cut.get_player_stars(["user1", "EpicWolverine", "user2"]))
        self.assertEqual({"merc1": 4, "Mautamu": 3}, self.cut.get_merc_stars(self.cut.get_mercs()))

    def test_get_player_info(self):
        expected = {
            'active_team': {'name': 'Aldi'}, 'name': 'EpicWolverine', 'platform': 'reddit',
            'ratings': {'awards': 5, 'gameTurns': 3, 'mvps': 4, 'overall': 4, 'streak': 4, 'totalTurns': 5},
            'stats': {'awards': 5, 'gameTurns': 18, 'mvps': 10, 'streak': 18, 'totalTurns': 113},
            'team': {'name': 'Aldi'},
            'turns': [{'day': 18, 'mvp': True, 'season': 1, 'stars': 4, 'team': 'Aldi', 'territory': 'Alaska'},
                      {'day': 17, 'mvp': False, 'season': 1, 'stars': 4, 'team': 'Aldi', 'territory': 'Minnesota'}]}
        self.assertEqual(expected, self.cut.get_player_info("EpicWolverine"))

    def test_get_batch_player_info(self):
        self.maxDiff = None
        expected = [
            {'name': 'EpicWolverine', 'platform': 'reddit',
            'ratings': {'awards': 5, 'gameTurns': 3, 'mvps': 4, 'overall': 4, 'streak': 4, 'totalTurns': 5},
            'stats': {'awards': 5, 'gameTurns': 18, 'mvps': 10, 'streak': 18, 'totalTurns': 113},
            'team': {'name': 'Aldi'},
            'turns': [{'day': 18, 'mvp': True, 'season': 1, 'stars': 4, 'team': 'Aldi', 'territory': 'Alaska'},
                      {'day': 17, 'mvp': False, 'season': 1, 'stars': 4, 'team': 'Aldi', 'territory': 'Minnesota'}]},
            {"name": "Mautamu", "team": {"name": "Texas A&M"}, "platform": "reddit",
             "ratings": {"overall": 1, "totalTurns": 3, "gameTurns": 1, "mvps": 1, "streak": 1},
             "stats": {"totalTurns": 42, "gameTurns": 0, "mvps": 0, "streak": 0},
             "turns": [{"season": 2, "day": 50, "stars": 3, "mvp": False, "territory": "Stillwater", "team": "Texas A&M"}]}
        ]
        self.assertEqual(expected, self.cut.get_batch_player_info([{"player": "EpicWolverine"}, {"player": "Mautamu"}]))
        self.assertEqual(0, self.cut._get_player_api_data_access_count)
        self.assertEqual({"EpicWolverine": expected[0], "Mautamu": expected[1]}, self.cut.cache.player_info)

    def test_get_players_cache(self):
        self.cut.get_players()
        self.cut.get_players()
        self.assertEqual(1, self.cut._get_team_api_data_access_count["players"])

    def test_get_mercs_cache(self):
        self.cut.get_mercs()
        self.cut.get_mercs()
        self.assertEqual(1, self.cut._get_team_api_data_access_count["mercs"])

    def test_player_info_cache(self):
        self.cut.get_player_info("EpicWolverine")
        self.cut.get_player_info("EpicWolverine")
        self.assertEqual(1, self.cut._get_player_api_data_access_count)

    def test_get_previous_turn(self):
        expected = {"id": 19, "season": 1, "day": 19, "complete": True, "active": False, "finale": False, "rollTime": "2022-02-06T03:30:01.685073"}
        self.assertEqual(expected, self.cut.get_previous_turn())
