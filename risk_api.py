import json
import requests
import unittest


class ApiCache:
    def __init__(self):
        self.players = None
        self.mercs = None
        self.player_info = {}


class RiskApi:
    def __init__(self):
        self.cache = ApiCache()
        self.team = "Aldi"
        self.csv_name = "stars.csv"

    def _get_team_api_data(self, endpoint):
        api_url = f"https://collegefootballrisk.com/api/{endpoint}?team={self.team}"
        headers = {"Content-Type": "application/json"}
        response_json = requests.get(api_url, headers=headers).json()
        # print(response_json)
        return response_json

    def get_players(self):
        if self.cache.players is None:
            self.cache.players = self._get_team_api_data("players")
        return self.cache.players

    def get_mercs(self):
        if self.cache.mercs is None:
            self.cache.mercs = self._get_team_api_data("mercs")
        return self.cache.mercs

    def get_player_stars(self, players):
        player_stars = {}
        for player in players:
            player_name = player["player"]
            player_stars[player_name] = self.get_player_info(player_name)["ratings"]["overall"]
        return player_stars

    def get_merc_stars(self, mercs):
        merc_stars = {}
        for merc in mercs:
            merc_stars[merc["player"]] = merc["stars"]
        return merc_stars

    def _get_player_api_data(self, player_name):
        api_url = f"https://collegefootballrisk.com/api/player?player={player_name}"
        headers = {"Content-Type": "application/json"}
        response_json = requests.get(api_url, headers=headers).json()
        # print(response_json)
        return response_json

    def get_player_info(self, player_name):
        if player_name not in self.cache.player_info or self.cache.player_info[player_name] is None:
            self.cache.player_info[player_name] = self._get_player_api_data(player_name)
        return self.cache.player_info[player_name]

    def generate_csv(self):
        stars = {}
        stars.update(self.get_player_stars(self.get_players()))
        stars.update(self.get_merc_stars(self.get_mercs()))
        csv = "Reddit Name,Stars,Last Day Played\n"
        for player in stars:
            player_info = self.get_player_info(player)
            last_day_played = 0
            player_turns = player_info["turns"]
            if len(player_turns) > 0:
                last_day_played = player_turns[0]["day"]
            csv += f"{player},{stars[player]},{last_day_played}\n"
        return csv

    def write_csv_file(self):
        with open(self.csv_name, "w") as file:
            file.write(self.generate_csv())


class MockRiskApi(RiskApi):
    def _get_team_api_data(self, endpoint):
        response = ""
        if endpoint == "players":
            response = '[{"team": "Aldi", "player": "user1", "turnsPlayed": 16, "mvps": 6, "lastTurn": {"season": 1, "day": 17, "stars": 3}}, {"team": "Aldi", "player": "EpicWolverine", "turnsPlayed": 112, "mvps": 9, "lastTurn": {"season": 1, "day": 17, "stars": 4}}, {"team": "Aldi","player": "user2","turnsPlayed": 92,"mvps": 12,"lastTurn": {"season": -1,"day": 116,"stars": 4}}]'
        elif endpoint == "mercs":
            response = '[{"team": "Aldi", "player": "merc1", "turnsPlayed": 67, "mvps": 6, "stars": 4}, {"team": "Aldi", "player": "Mautamu", "turnsPlayed": 57, "mvps": 6, "stars": 3}]'
        else:
            return super()._get_team_api_data(endpoint)
        return json.loads(response)

    def _get_player_api_data(self, player_name):
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


class TestSuite(unittest.TestCase):
    def setUp(self) -> None:
        self.cut = MockRiskApi()

    def test_get_players(self):
        self.assertIsNotNone(self.cut.get_players())
        self.assertIsNotNone(self.cut.get_mercs())

    def test_stars(self):
        self.assertEqual(self.cut.get_player_stars(self.cut.get_players()), {"user1": 4, "EpicWolverine": 4, "user2": 4})
        self.assertEqual(self.cut.get_merc_stars(self.cut.get_mercs()), {"merc1": 4, "Mautamu": 3})

    def test_get_player_info(self):
        expected = {
            'active_team': {'name': 'Aldi'},
            'name': 'EpicWolverine',
            'platform': 'reddit',
            'ratings': {'awards': 5,
                        'gameTurns': 3,
                        'mvps': 4,
                        'overall': 4,
                        'streak': 4,
                        'totalTurns': 5},
            'stats': {'awards': 5,
                      'gameTurns': 18,
                      'mvps': 10,
                      'streak': 18,
                      'totalTurns': 113},
            'team': {'name': 'Aldi'},
            'turns': [{'day': 18,
                       'mvp': True,
                       'season': 1,
                       'stars': 4,
                       'team': 'Aldi',
                       'territory': 'Alaska'},
                      {'day': 17,
                       'mvp': False,
                       'season': 1,
                       'stars': 4,
                       'team': 'Aldi',
                       'territory': 'Minnesota'}]}
        self.assertEqual(self.cut.get_player_info("EpicWolverine"), expected)

    def test_csv_generation(self):
        expected = "Reddit Name,Stars,Last Day Played\nuser1,4,18\nEpicWolverine,4,18\nuser2,4,0\nmerc1,4,18\nMautamu,3,16\n"
        self.assertEqual(self.cut.generate_csv(), expected)


if __name__ == "__main__":
    api = RiskApi()
    api.write_csv_file()
    # players = api.get_players()
    # for player in players:
    #     player_info = api.get_player_info(player["player"])
    #     if player["lastTurn"]["stars"] != player_info["ratings"]["overall"]:
    #         print(f"{player['player']} lasturn stars != current stars: {player['lastTurn']['stars']} != {player_info['ratings']['overall']}")
    #         print(player_info)
