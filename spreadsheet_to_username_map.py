import json
import unittest


class Main:
    def __init__(self):
        self.players_csv = "Risk Tracking Sheet - Wolverines.csv"
        self.diplomats_csv = "Risk Tracking Sheet - Diplomats.csv"
        self.json_path = "username_map.json"

    @staticmethod
    def read_csv(path: str) -> list[dict]:
        rows = []
        with open(path, 'r', encoding='utf-8') as file:
            header = file.readline().strip().split(',')
            for line in file:
                rows.append({key: value for key, value in zip(header, line.strip().split(','))})
        return rows

    @staticmethod
    def extract_players(csv: list[dict[str, str]]) -> dict[str, dict[str, dict]]:
        prefix_column = "Discord Nickname Prefix"
        update_nickname_column = "Update Discord Nickname with Bot?"
        discord_id_column = "Discord ID"
        reddit_username_column = "Reddit"
        reason_column = "Notes"
        mapping = {"players": {}, "exclude": {}}
        for row in csv:
            if row[discord_id_column] and row[reddit_username_column]:
                category = "players" if row[update_nickname_column] == "Yes" else "exclude"
                mapping[category][row[discord_id_column]] = {"reddit": row[reddit_username_column],
                                                             "prefix": row[prefix_column]}
                if row[reason_column]:
                    mapping[category][row[discord_id_column]]["reason"] = row[reason_column]
        return mapping

    @staticmethod
    def extract_diplomats(csv: list[dict[str, str]]) -> dict[str, dict[str, dict]]:
        nickname_column = "Discord Nickname"
        team_column = "Team"
        discord_id_column = "Discord ID"
        diplomats = {}
        for row in csv:
            if row[discord_id_column]:
                diplomats[row[discord_id_column]] = {"nickname": row[nickname_column],
                                                     "team": row[team_column]}
        return {"diplomats": diplomats}

    @staticmethod
    def write_json(path: str, obj: dict[str, dict[str, dict]]):
        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(json.dumps(obj, indent=4))

    def main(self):
        players = self.extract_players(self.read_csv(self.players_csv))
        diplomats = self.extract_diplomats(self.read_csv(self.diplomats_csv))
        username_map = players | diplomats
        self.write_json(self.json_path, username_map)


class TestSuite(unittest.TestCase):
    def setUp(self) -> None:
        self.cut = Main()
        self.cut.players_csv = "unittests/Risk Tracking Sheet - Players.csv"
        self.cut.diplomats_csv = "unittests/Risk Tracking Sheet - Diplomats.csv"
        self.players_csv_expected = [
            {"Discord Nickname": "other name", "Discord Name": "not me#3742", "Discord Nickname Prefix": "prefix",
             "Update Discord Nickname with Bot?": "Yes", "Discord ID": "1234567890", "Reddit": "PM_me_your_moves",
             "Notes": ""},
            {"Discord Nickname": "", "Discord Name": "EpicWolverine#3742", "Discord Nickname Prefix": "EpicWolverine",
             "Update Discord Nickname with Bot?": "No", "Discord ID": "140174746485653504", "Reddit": "EpicWolverine",
             "Notes": "Script cannot update server owner's nickname"},
            {'Discord ID': '', 'Discord Name': '', 'Discord Nickname': '', 'Discord Nickname Prefix': '',
             'Notes': '', 'Reddit': '', 'Update Discord Nickname with Bot?': 'Yes'}
        ]

    def test_read_csv(self):
        self.assertEqual(self.players_csv_expected, self.cut.read_csv(self.cut.players_csv))

    def test_extract_players(self):
        expected = {
            "players": {
                "1234567890": {"prefix": "prefix", "reddit": "PM_me_your_moves"},
            },
            "exclude": {
                "140174746485653504": {"prefix": "EpicWolverine", "reddit": "EpicWolverine",
                                       "reason": "Script cannot update server owner's nickname"},
            }
        }
        self.assertEqual(expected, self.cut.extract_players(self.players_csv_expected))

    def test_extract_diplomats(self):
        expected = {
            "diplomats": {
                "1234567890": {"nickname": "Larry Scott", "team": "NCAA"},
            },
        }
        self.assertEqual(expected, self.cut.extract_diplomats(self.cut.read_csv(self.cut.diplomats_csv)))


if __name__ == "__main__":
    main = Main()
    main.main()
