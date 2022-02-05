import json
import requests
import unittest


class ApiCache:
    def __init__(self):
        self.players = None
        self.mercs = None


class RiskApi:
    def __init__(self):
        self.cache = ApiCache()
        self.team = "Aldi"
        self.csv_name = "stars.csv"

    def get_team_api_data(self, endpoint):
        api_url = f"https://collegefootballrisk.com/api/{endpoint}?team={self.team}"
        headers = {"Content-Type": "application/json"}
        response_json = requests.get(api_url, headers=headers).json()
        # print(response_json)
        return response_json

    def get_players(self):
        if self.cache.players is None:
            self.cache.players = self.get_team_api_data("players")
        return self.cache.players

    def get_mercs(self):
        if self.cache.mercs is None:
            self.cache.mercs = self.get_team_api_data("mercs")
        return self.cache.mercs

    def get_player_stars(self, players):
        player_stars = {}
        for player in players:
            player_stars[player["player"]] = player["lastTurn"]["stars"]
        return player_stars

    def get_merc_stars(self, mercs):
        merc_stars = {}
        for merc in mercs:
            merc_stars[merc["player"]] = merc["stars"]
        return merc_stars

    def generate_csv(self):
        stars = {}
        stars.update(self.get_player_stars(self.get_players()))
        stars.update(self.get_merc_stars(self.get_mercs()))
        csv = ""
        for star in stars:
            csv += f"{star},{stars[star]}\n"
        return csv

    def write_csv_file(self):
        with open(self.csv_name, "w") as file:
            file.write(self.generate_csv())


class MockRiskApi(RiskApi):
    def get_team_api_data(self, endpoint):
        response = ""
        if endpoint == "players":
            response = '[{"team": "Aldi", "player": "user1", "turnsPlayed": 16, "mvps": 6, "lastTurn": {"season": 1, "day": 17, "stars": 3}}, {"team": "Aldi", "player": "EpicWolverine", "turnsPlayed": 112, "mvps": 9, "lastTurn": {"season": 1, "day": 17, "stars": 4}}]'
        elif endpoint == "mercs":
            response = '[{"team": "Aldi", "player": "merc1", "turnsPlayed": 67, "mvps": 6, "stars": 4}, {"team": "Aldi", "player": "Mautamu", "turnsPlayed": 57, "mvps": 6, "stars": 3}]'
        else:
            return super().get_team_api_data(endpoint)
        return json.loads(response)


class TestSuite(unittest.TestCase):
    def setUp(self) -> None:
        self.cut = MockRiskApi()

    def test_get_players(self):
        self.assertIsNotNone(self.cut.get_players())
        self.assertIsNotNone(self.cut.get_mercs())

    def test_stars(self):
        self.assertEqual(self.cut.get_player_stars(self.cut.get_players()), {"user1": 3, "EpicWolverine": 4})
        self.assertEqual(self.cut.get_merc_stars(self.cut.get_mercs()), {"merc1": 4, "Mautamu": 3})

    def test_csv_generation(self):
        expected = "user1,3\nEpicWolverine,4\nmerc1,4\nMautamu,3\n"
        self.assertEqual(self.cut.generate_csv(), expected)


if __name__ == "__main__":
    api = RiskApi()
    api.write_csv_file()
