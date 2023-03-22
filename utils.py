from jinja2 import Template


def build_html_string(
    player: str,
    opponent: str,
    update_time: str,
    all_time_matches: int,
    player_total_wins: int,
    opponent_total_wins: int,
    latest_game_date: str,
    player_latest_date_wins: int,
    opponent_latest_date_wins: int,
) -> str:
    with open("template.html") as f:
        template_str = f.read()
    template = Template(template_str)
    html_string = template.render(
        player=player,
        opponent=opponent,
        player_name=player.split("%")[0],
        opponent_name=opponent.split("%")[0],
        update_time=update_time,
        all_time_matches=all_time_matches,
        player_total_wins=player_total_wins,
        opponent_total_wins=opponent_total_wins,
        player_percent=round(player_total_wins / all_time_matches, 3),
        opponent_percent=round(opponent_total_wins / all_time_matches, 3),
        latest_game_date=latest_game_date,
        player_latest_date_wins=player_latest_date_wins,
        opponent_latest_date_wins=opponent_latest_date_wins,
        player_image_url=player.split("%")[0].lower() + ".jpg",
        opponent_image_url=opponent.split("%")[0].lower() + ".jpg",
    )
    return html_string


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


def build_new_leaderboard_file_data(
    player: str,
    opponent: str,
    update_time: str,
    all_time_matches: int,
    player_total_wins: int,
    opponent_total_wins: int,
    latest_game_date: str,
    latest_date_matches: int,
    player_latest_date_wins: int,
    opponent_latest_date_wins: int,
):
    new_leaderboard_file_data = []
    new_leaderboard_file_data.append("last updated: " + update_time + "\n\n")
    new_leaderboard_file_data.append("ALL-TIME\n")
    new_leaderboard_file_data.append("Matches: " + str(all_time_matches) + "\n\n")
    new_leaderboard_file_data.append(
        player
        + ": "
        + str(player_total_wins)
        + " ("
        + str(round(player_total_wins / all_time_matches, 3))
        + ")"
        + "\n"
    )
    new_leaderboard_file_data.append(
        opponent
        + ": "
        + str(opponent_total_wins)
        + " ("
        + str(round(opponent_total_wins / all_time_matches, 3))
        + ")"
        + "\n"
    )
    new_leaderboard_file_data.append("\n")
    new_leaderboard_file_data.append("TODAY (" + latest_game_date + ")" + "\n")
    new_leaderboard_file_data.append("Matches: " + str(latest_date_matches) + "\n\n")
    new_leaderboard_file_data.append(
        player + ": " + str(player_latest_date_wins) + "\n"
    )
    new_leaderboard_file_data.append(
        opponent + ": " + str(opponent_latest_date_wins) + "\n"
    )
    new_leaderboard_file_data.append("\n")

    return new_leaderboard_file_data
