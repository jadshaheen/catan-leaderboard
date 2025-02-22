from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import argparse
import time

from utils import (
    build_html_string,
    get_current_leaderboard_data,
    build_new_leaderboard_file_data,
)

BASE_URL = "https://colonist.io/profile/{}#history"

# uncomment the second path in both of the following for testing purposes,
# so as not to corrupt the actual files the leaderboard uses
LEADERBOARD_FILEPATH = (
    "/Users/jad/Desktop/projects/jadshaheen.github.io/catan/leaderboard_{}_{}.txt"
)
LEADERBOARD_HTML_DISPLAY_FILEPATH = (
    "/Users/jad/Desktop/projects/jadshaheen.github.io/catan/{}_{}.html"
)

CHROME_DRIVER_PATH = "./chromedriver"

player_to_name = {
    "Abhi0875": "Abhi",
    "Abhi#6004": "Abhi",
    "Saquon": "Zaki",
    "JBlova": "Lali",
    "pill": "AJ",
    "viri": "Virindh",
    "jad": "Jad",
    "umzaki": "Mom",
    "Dinin0213": "Mansi",
}


def get_game_history_table(player):
    """
    Returns a list where each item is an HTML <tr> element representing one match in PLAYER's
    last 100 games
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)

    table_rows = None

    # <tbody> element loads immediately, but actual table rows take a second to load, so we do this while loop.
    # Ideally, we would replace this with a selenium explicit wait, and create an Expected Condition method
    # which checks for the presence of children <tr> elements of the <tbody>.
    attempt_num = 1
    while not table_rows and attempt_num <= 5:
        driver.get(BASE_URL.format(player.replace("#", "%23")))
        # Instead of using driver.implicitly_wait, we sleep here instead. The above driver.get line loads the website, but it's only when we
        # explicitly ask for the page source (on the next line) that the html is grabbed. So this is more confident way to make sure the tbody
        # appears, without necessitating the while loop (we leave the loop for now for testing).
        time.sleep(4)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("tbody", {"id": "game-history-table-body"})
        table_rows = table.find_all("tr", recursive=False)
        attempt_num += 1

    return table_rows


def filter_rows(table_rows, opponent, last_updated):
    """
    Filter out all matches that aren't against OPPONENT or completed before LAST_UPDATED timestamp.
    """
    data = []

    for i in range(len(table_rows))[::2]:
        datum = {}
        for index, col in enumerate(table_rows[i].find_all("td")):
            if index == 0:
                datum["time"] = col.text
            elif index == 3:
                datum["duration"] = col.text

        secondary_table = (
            table_rows[i + 1]
            .find("table", {"class": "game-details-table"})
            .find_all("tr")
        )
        players = []
        ranks = []
        datum["finished"] = True
        for row in secondary_table:
            cols = row.find_all("td")
            for index, col in enumerate(cols):
                if index == 0:
                    players.append(col.text)
                if index == 1:
                    ranks.append(col.text)
                if index == 3:
                    finished = col.find("img", alt=True)["alt"]
                    if finished == "X":
                        datum["finished"] = False
        datum["players"] = players
        datum["ranks"] = ranks

        data.append(datum)

    # Colonist stores the START time of each game; for our script to work, we update the time for each match row to be the start time plus the
    # duration, effectively resulting in the END time. This allows our script to not overlook games which were in progress when an update was triggered.
    data = [
        {
            **row,
            "end_time": str(
                datetime.strptime(
                    row.get("time").replace("24:", "00:"), "%m/%d/%Y, %H:%M"
                )
                + timedelta(
                    minutes=int(row.get("duration").split(":")[0]),
                    seconds=int(row.get("duration").split(":")[1]),
                )
            ),
        }
        for row in data
    ]

    # filter out unfinished games
    filtered_data = [row for row in data if row.get("finished")]

    # filter out games that don't involve 'opponent'
    filtered_data = [row for row in filtered_data if opponent in row.get("players")]
    # filter out games that ENDED before LAST_UPDATED (aka would already have been included in leaderboard)
    filtered_data = [row for row in filtered_data if row.get("end_time") > last_updated]

    return filtered_data


def get_num_wins(match_data, player, opponent):
    wins_dict = {player: 0, opponent: 0}

    for match in match_data:
        player_rank, opp_rank = 0, 0
        for player_name, rank in zip(match.get("players"), match.get("ranks")):
            if player_name == player:
                player_rank = int(rank.split("/")[0])
            if player_name == opponent:
                opp_rank = int(rank.split("/")[0])

        if player_rank < opp_rank:
            wins_dict[player] += 1
        else:
            wins_dict[opponent] += 1

    return wins_dict


def update_leaderboard(args, leaderboard_filepath, html_filepath):
    player, opponent = args.player, args.opponent

    if args.test:
        leaderboard_filepath = "/Users/jad/Desktop/catan_leaderboard_test.txt"
        html_filepath = "/Users/jad/Desktop/catan_test.html"

    current_leaderboard_data = get_current_leaderboard_data(leaderboard_filepath)

    new_leaderboard_file_data = []

    print(
        "Updating Catan Leaderboard data for "
        + player_to_name[player]
        + " and "
        + player_to_name[opponent]
        + "..."
    )
    update_time = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    game_history = get_game_history_table(player)

    if game_history == None:
        # This can occur when the colonist website itself is having problems and unable to display profile data
        print("ERROR 500: Unable to locate data on server")

    else:
        matches = filter_rows(
            game_history, opponent, current_leaderboard_data.get("last_updated")
        )
        # Don't try to update if no games have been played since last update
        if len(matches) > 0:
            wins_dict = get_num_wins(matches, player, opponent)

            total_matches = current_leaderboard_data.get(
                "player_wins"
            ) + current_leaderboard_data.get("opponent_wins")
            daily_matches = current_leaderboard_data.get(
                "daily_player_wins"
            ) + current_leaderboard_data.get("daily_opponent_wins")

            # update overall leaderboard
            updated_total_matches = sum(wins_dict.values()) + total_matches
            player_total_wins = wins_dict.get(player) + current_leaderboard_data.get(
                "player_wins"
            )
            opponent_total_wins = wins_dict.get(
                opponent
            ) + current_leaderboard_data.get("opponent_wins")

            # update daily leaderboard
            # Retrieve latest date of NEW game played which will be date of first element in matches (below)
            latest_game_date = matches[0].get("end_time").split(" ")[0]
            latest_date_matches, player_latest_date_wins, opponent_latest_date_wins = (
                0,
                0,
                0,
            )

            # consolidate this if/else so we dont repeat logic but just use the right wins_dict (either total or latest_date)
            if (
                latest_game_date
                == current_leaderboard_data.get("daily_leaderboard_date").split(" ")[0]
            ):
                latest_date_matches = sum(wins_dict.values()) + daily_matches
                player_latest_date_wins = wins_dict.get(
                    player
                ) + current_leaderboard_data.get("daily_player_wins")
                opponent_latest_date_wins = wins_dict.get(
                    opponent
                ) + current_leaderboard_data.get("daily_opponent_wins")
            else:
                latest_date_match_list = [
                    match
                    for match in matches
                    if match.get("end_time").split(" ")[0] == latest_game_date
                ]
                latest_date_wins_dict = get_num_wins(
                    latest_date_match_list, player, opponent
                )
                latest_date_matches = sum(latest_date_wins_dict.values())
                (
                    player_latest_date_wins,
                    opponent_latest_date_wins,
                ) = latest_date_wins_dict.get(player), latest_date_wins_dict.get(
                    opponent
                )

            new_leaderboard_file_data = build_new_leaderboard_file_data(
                player=player_to_name[player],
                opponent=player_to_name[opponent],
                update_time=update_time,
                all_time_matches=updated_total_matches,
                player_total_wins=player_total_wins,
                opponent_total_wins=opponent_total_wins,
                latest_game_date=latest_game_date,
                latest_date_matches=latest_date_matches,
                player_latest_date_wins=player_latest_date_wins,
                opponent_latest_date_wins=opponent_latest_date_wins,
            )

            with open(leaderboard_filepath, "w") as file:
                for line in new_leaderboard_file_data:
                    file.write(line)

            with open(html_filepath, "w") as file:
                html_string = build_html_string(
                    player=player_to_name[player],
                    opponent=player_to_name[opponent],
                    update_time=update_time,
                    all_time_matches=updated_total_matches,
                    player_total_wins=player_total_wins,
                    opponent_total_wins=opponent_total_wins,
                    latest_game_date=latest_game_date,
                    player_latest_date_wins=player_latest_date_wins,
                    opponent_latest_date_wins=opponent_latest_date_wins,
                )
                file.write(html_string)

            print("Leaderboard updated!")
        else:
            print("Already up to date!")
            """
            If the --force option is given, update last_updated time to reflect that leaderboard is accurate as of now,
            even though no new data was added. If provided in the cronjob, this means a new commit will be published at
            each run.
            """
            if args.force:
                with open(leaderboard_filepath, "r") as file:
                    cur_file_lines = file.readlines()
                    new_leaderboard_file_data = [
                        cur_file_lines[0].split(": ")[0] + ": " + update_time + "\n"
                    ] + cur_file_lines[1:]
                with open(leaderboard_filepath, "w") as file:
                    for line in new_leaderboard_file_data:
                        file.write(line)
                with open(html_filepath, "w") as file:
                    html_string = build_html_string(
                        player=player_to_name[player],
                        opponent=player_to_name[opponent],
                        update_time=update_time,
                        all_time_matches=current_leaderboard_data.get("player_wins")
                        + current_leaderboard_data.get("opponent_wins"),
                        player_total_wins=current_leaderboard_data.get("player_wins"),
                        opponent_total_wins=current_leaderboard_data.get(
                            "opponent_wins"
                        ),
                        latest_game_date=current_leaderboard_data.get(
                            "daily_leaderboard_date"
                        ),
                        player_latest_date_wins=current_leaderboard_data.get(
                            "daily_player_wins"
                        ),
                        opponent_latest_date_wins=current_leaderboard_data.get(
                            "daily_opponent_wins"
                        ),
                    )
                    file.write(html_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Use this script to update catan leaderboards at jadshaheen.com."
    )
    parser.add_argument(
        "player", help="Colonist username of first player on leaderboard"
    )
    parser.add_argument(
        "opponent", help="Colonist username of second player on leaderboard"
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Instead of updating the actual files the website uses, if this flag is present update two dummy files on my Desktop",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force rewriting the files even if there is no new game data",
    )

    args = parser.parse_args()

    leaderboard_path = LEADERBOARD_FILEPATH.format(
        player_to_name[args.player].lower(), player_to_name[args.opponent].lower()
    )
    html_path = LEADERBOARD_HTML_DISPLAY_FILEPATH.format(
        player_to_name[args.player].lower(), player_to_name[args.opponent].lower()
    )

    update_leaderboard(args, leaderboard_path, html_path)
