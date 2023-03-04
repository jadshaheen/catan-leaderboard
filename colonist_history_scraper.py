from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

from utils import build_html_string, build_new_leaderboard_file_data

BASE_URL = "https://colonist.io/profile/{}#history"

# uncomment the second path in both of the following for testing purposes,
# so as not to corrupt the actual files the leaderboard uses
LEADERBOARD_FILEPATH = (
    "/Users/jad/Desktop/projects/jadshaheen.github.io/catan/catan_leaderboard.txt"
    # "/Users/jad/Desktop/catantime.txt"
)
LEADERBOARD_HTML_DISPLAY_FILEPATH = (
    "/Users/jad/Desktop/projects/jadshaheen.github.io/catan.html"
    # "/Users/jad/Desktop/catanhtml.txt"
)


def get_game_history_table(player):
    """
    Returns a list where each item is an HTML <tr> element representing one match in USER's
    last 100 games
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    table_rows = None

    # <tbody> element loads immediately, but actual table rows take a second to load, so we do this while loop.
    # Ideally, we would replace this with a selenium explicit wait, and create an Expected Condition method
    # which checks for the presence of children <tr> elements of the <tbody>.
    attempt_num = 1
    while not table_rows and attempt_num <= 5:
        driver.get(BASE_URL.format(player))
        # Instead of using driver.implicitly_wait, we sleep here instead. The above driver.get line loads the website, but it's only when we
        # explicitly ask for the page source (on the next line) that the html is grabbed. So this is more confident way to make sure the tbody
        # appears, without necessitating the while loop (we leave the loop for now for testing).
        time.sleep(4)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("tbody", {"id": "profile_games_table"})
        table_rows = table.find_all("tr", recursive=False)
        attempt_num += 1

    return table_rows


def filter_rows(table_rows, opponent, last_updated):
    """
    Filter out all matches that aren't against OPPONENT or completed before LAST_UPDATED timestamp.
    """
    data = []

    for i in range(len(table_rows))[::2]:
        datum = [col.text for col in table_rows[i].find_all("td")]
        secondary_table = [col.text for col in table_rows[i + 1].find_all("td")]
        # secondary table is of the form [..., opponent, '', rank]
        for j in range(len(secondary_table)):
            if secondary_table[j].strip() == opponent:
                datum.append(secondary_table[j + 2])
        data.append(datum)

    # Colonist stores the START time of each game; for our script to work, we update the time for each match row to be the start time plus the
    # duration, effectively resulting in the END time. This allows our script to not overlook games which were in progress when an update was triggered.
    data = [
        [
            str(
                datetime.strptime(row[0], "%m/%d/%Y, %I:%M:%S %p")
                + timedelta(
                    minutes=int(row[4].split(":")[0]), seconds=int(row[4].split(":")[1])
                )
            )
        ]
        + row[1:]
        for row in data
    ]

    # filter out games that don't involve 'opponent'
    filtered_data = [row for row in data if opponent in row[6].split(" ")]
    # filter out games that ENDED before LAST_UPDATED (aka would already have been included in leaderboard)
    filtered_data = [datum for datum in filtered_data if datum[0] > last_updated]

    return filtered_data


def get_num_wins(match_data, player, opponent):
    wins_dict = {player: 0, opponent: 0}

    for match in match_data:
        if int(match[1].split("/")[0]) < int(match[-1].split("/")[0]):
            wins_dict[player] += 1
        else:
            wins_dict[opponent] += 1

    return wins_dict


def get_current_leaderboard_data(filepath):
    current_leaderboard_data = {
        "last_updated": "1970-01-01 00:00:00",
        "player_wins": 0,
        "opponent_wins": 0,
        "daily_leaderboard_date": "1970-01-01 00:00:00",
        "daily_player_wins": 0,
        "daily_opponent_wins": 0,
    }

    try:
        file = open(filepath, "r")
        lines = file.readlines()
        real_lines = [line for line in lines if line != "\n"]
        current_leaderboard_data["last_updated"] = (
            real_lines[0].split(": ")[1].strip("\n")
        )
        current_leaderboard_data["player_wins"] = int(
            real_lines[3].split(": ")[1].split(" ")[0]
        )
        current_leaderboard_data["opponent_wins"] = int(
            real_lines[4].split(": ")[1].split(" ")[0]
        )
        current_leaderboard_data["daily_leaderboard_date"] = (
            real_lines[5].split(" ")[1].strip("()\n")
        )
        current_leaderboard_data["daily_player_wins"] = int(
            real_lines[7].split(": ")[1]
        )
        current_leaderboard_data["daily_opponent_wins"] = int(
            real_lines[8].split(": ")[1]
        )
    except FileNotFoundError:
        pass

    return current_leaderboard_data


if __name__ == "__main__":
    player, opponent = "viri", "jad"

    current_leaderboard_data = get_current_leaderboard_data(LEADERBOARD_FILEPATH)

    time_since_last_refresh = datetime.now() - datetime.strptime(
        current_leaderboard_data.get("last_updated"), "%Y-%m-%d %H:%M:%S"
    )
    time_since_last_refresh = time_since_last_refresh.total_seconds()

    new_leaderboard_file_data = []

    print("Updating Catan Leaderboard data...")
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
            latest_game_date = matches[0][0].split(" ")[0]
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
                    if match[0].split(" ")[0] == latest_game_date
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
                player=player,
                opponent=opponent,
                update_time=update_time,
                all_time_matches=updated_total_matches,
                player_total_wins=player_total_wins,
                opponent_total_wins=opponent_total_wins,
                latest_game_date=latest_game_date,
                latest_date_matches=latest_date_matches,
                player_latest_date_wins=player_latest_date_wins,
                opponent_latest_date_wins=opponent_latest_date_wins,
            )

            with open(LEADERBOARD_FILEPATH, "w") as file:
                for line in new_leaderboard_file_data:
                    file.write(line)

            with open(LEADERBOARD_HTML_DISPLAY_FILEPATH, "w") as file:
                html_string = build_html_string(
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
            Uncomment the below code to update last_updated time to reflect that leaderboard is accurate as of now,
            even though no new data was added. This means a new commit will be published at each cronjob run.
            """
            # with open(LEADERBOARD_FILEPATH, "r") as file:
            #     cur_file_lines = file.readlines()
            #     new_leaderboard_file_data = [
            #         cur_file_lines[0].split(": ")[0] + ": " + update_time + "\n"
            #     ] + cur_file_lines[1:]
            # with open(LEADERBOARD_FILEPATH, "w") as file:
            #     for line in new_leaderboard_file_data:
            #         file.write(line)
            # with open(LEADERBOARD_HTML_DISPLAY_FILEPATH, "w") as file:
            #     html_string = build_html_string(
            #         update_time,
            #         current_leaderboard_data.get("player_wins")
            #         + current_leaderboard_data.get("opponent_wins"),
            #         current_leaderboard_data.get("player_wins"),
            #         current_leaderboard_data.get("opponent_wins"),
            #         current_leaderboard_data.get("daily_leaderboard_date"),
            #         current_leaderboard_data.get("daily_player_wins"),
            #         current_leaderboard_data.get("daily_opponent_wins"),
            #     )
            #     file.write(html_string)
