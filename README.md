# CFBRiskMoveTracker

Make move orders and allocation for your CFB Risk team easier. This script logs all players and mercs on your team, how many stars they have, and when they last played. It also updates players' nicknames a connected discord server with their current star count. Set up as a scheduled task to run several minutes after the day's roll.

Written for Team Aldi as part of the Grocery Store Beta.

# Set Up
1. Clone/download this repository.
2. Install Python if needed.
3. Create a Python virtual environment and install `requirements.txt`.
   ```powershell
   cd CFBRiskMoveTracker
   py.exe -m venv venv
   .\venv\Scripts\activate.ps1
   python.exe -m pip install --upgrade pip
   pip install -r .\requirements.txt
   ```
5. Create a Discord application at https://discord.com/developers/applications
6. Under OAuth2, copy the Client ID into your `settings.json` (see below).
7. Under Bot, create a bot and enable the Server Members Intent (also called `GUILD_MEMBERS`).   
  ![image](https://github.com/EpicWolverine/CFBRiskMoveTracker/assets/2897970/9e14823c-2d29-436c-a2d5-25da5d504d4d)
8. Copy the bot's token into your `settings.json` (see below).
9. In Discord, got to Settings -> Advanced -> turn on Developer Mode. This lets you right-click on most things and copy their internal ID.
10. Right-click on your server, click Copy ID, and paste into your `settings.json` under `guild_id` (see below).
11. Create a `username_map.json` and fill it out with users' Discord IDs and Reddit usernames. See below for details.
12. Run `py.exe main.py -auth` to add the bot to your server.
13. Move the bot's role to the top of the list, or at least above everyone whose nickname you want to be able to change.
14. Run `py.exe main.py -prod` manually and see if it works!
15. Set up a scheduled task (or cron job) that runs the script 5 to 10 minutes after the day's roll. On Windows, that will look like `venv\Scripts\python.exe .\main.py -prod >> output.log 2>>errors.log`. This creates an `output.log` and `errors.log` in addition to the `script.log` in case anything goes horribly wrong.
16. You will need to add any new people that join your team and Discord server to `username_map.json`. See `script.log` for any errors.

# Details

```
> py.exe .\main.py --help
usage: main.py [-h] [-auth] [-nick] [-test_nick] [-prod]

Automate logging and setting Risk Stars. Default: Generate stars CSV and update Discord nicknames.

options:
  -h, --help            show this help message and exit
  -auth, --authenticate
                        Only open bot authentication link.
  -nick, --nickname     Only update Discord nicknames.
  -test_nick, --test_nickname
                        Only test Discord nickname updating.
  -prod, --use_prod_guild
                        Use production guild.
```

### `settings.json`
Stores various keys that should never be shared with anyone!  
Create a file named `settings.json` in this script's folder and paste the following. Replace descriptions with the needed values as described in [Set Up](#set-up).
`verified_discord_role_name` is the Discord role name for verified team players. Players with this role will be marked True in the "Has Verified Role" CSV column.
```JSON
{
    "settings": {
        "team": "Aldi",
        "verified_discord_role_name": "Wolverine"
    },
    "secrets": {
        "client_id": "from registering your bot",
        "bot_token": "from registering your bot",
        "guild_id": "the Discord server used with -prod",
        "test_guild_id": "the Discord server used by default during development",
        "test_user_id": "the Discord user to change when using -test_nick"
    }
}
```

### `username_map.json` and `test_username_map.json`
Stores the Discord User ID <-> Reddit username mappings.  
Create a file named `username_map.json` in this script's folder and paste the following. `test_username_map.json` is used for the test server when running the script in test mode (without `-prod`).  
Nicknames will be formatted as `prefix|reddit_name ⭐⭐⭐⭐⭐`. `prefix` is optional and ideal for people who want to go by another name on Discord.  
Only the Discord User ID is used in the `exclude` section. You can use the key values for whatever notes you want, such as what their nickname is on Discord or why they are excluded. Ideal for people who do not want their nickname changed automatically and for other bots.  
**WARNING:** The server owner cannot have their nickname changed by anyone but themselves, including bots. This is a Discord restriction. Add their Discord ID to the exclude list to suppress errors.
```JSON
{
    "players": {
        "12345678901234567890": {"reddit": "PM_me_your_risk_moves", "prefix": "John"},
        "09876543210987654231": {"reddit": "xX_360NoScope_Xx"}
    },
    "exclude": {
        "67890123456789012345": {"reddit": "EpicWolverine", "reason": "Server Owner cannot have nickname changed by bots"},
        "228537642583588864": {"nick": "Music Bot"}
    },
    "diplomats": {
        "111111111111111111": {"nickname": "Ag", "team": "Texas A&M"}
    }
}
```
