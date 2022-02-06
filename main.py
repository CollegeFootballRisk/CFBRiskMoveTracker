import unittest

from risk_api import RiskApi, MockRiskApi


class Main:
    def __init__(self):
        self.risk_api = RiskApi()
        self.csv_name = "stars.csv"

    def generate_csv(self):
        stars = {}
        stars.update(self.risk_api.get_player_stars(self.risk_api.get_players()))
        stars.update(self.risk_api.get_merc_stars(self.risk_api.get_mercs()))
        csv = "Reddit Name,Stars,Last Day Played\n"
        for player in stars:
            player_info = self.risk_api.get_player_info(player)
            last_day_played = 0
            player_turns = player_info["turns"]
            if len(player_turns) > 0:
                last_day_played = player_turns[0]["day"]
            csv += f"{player},{stars[player]},{last_day_played}\n"
        return csv

    def write_csv_file(self):
        with open(self.csv_name, "w") as file:
            file.write(self.generate_csv())


class TestSuite(unittest.TestCase):
    def setUp(self) -> None:
        self.cut = Main()
        self.cut.risk_api = MockRiskApi()

    def test_csv_generation(self):
        expected = "Reddit Name,Stars,Last Day Played\nuser1,4,18\nEpicWolverine,4,18\nuser2,4,0\nmerc1,4,18\nMautamu,3,16\n"
        self.assertEqual(self.cut.generate_csv(), expected)


if __name__ == "__main__":
    main = Main()
    main.write_csv_file()
