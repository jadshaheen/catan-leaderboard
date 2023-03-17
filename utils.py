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
):
    html_string = ""
    html_string += "<!DOCTYPE html>\n"
    html_string += "<html>\n"
    html_string += "  <head>\n"
    html_string += (
        '    <meta name="viewport" content="width=device-width, initial-scale=1" />\n'
    )
    html_string += "    <title>Catan Leaderboard</title>\n"
    html_string += '    <link rel="stylesheet" href="catan/catan.css" />\n'
    html_string += '    <link rel="icon" href="icon.png" />\n'
    html_string += "  </head>\n"
    html_string += "  <body>\n"
    html_string += "    <h1>Catan Leaderboard</h1>\n"
    html_string += "    <p><em>Last Updated: " + update_time + "</em></p>\n"
    html_string += '    <div class="contentdiv">\n'
    html_string += '      <div class="wins_display">\n'
    html_string += '        <div class="big_container">\n'
    html_string += (
        '          <h1 class="big_wins" id="left">' + str(player_total_wins) + "</h1>\n"
    )
    html_string += (
        '          <h2 class="big_percent">('
        + str(round(player_total_wins / all_time_matches, 3))
        + ")</h2>\n"
    )
    html_string += "        </div>\n"
    html_string += "      </div>\n"
    html_string += '      <div class="player">\n'
    html_string += '        <a href="https://colonist.io/profile/' + player + '">\n'
    html_string += (
        '          <img class="player_img" src="catan/' + player + '.jpg" />\n'
    )
    html_string += "        </a>\n"
    html_string += "      </div>\n"
    html_string += '      <div class="centerdivs">\n'
    html_string += '        <div class="allgames">\n'
    html_string += "          <p>All-Time Matches</p>\n"
    html_string += "          <h1>" + str(all_time_matches) + "</h1>\n"
    html_string += "        </div>\n"
    html_string += '        <div class="logo">\n'
    html_string += '          <a href="https://colonist.io">\n'
    html_string += '            <img class="logo_img" src="catan/catan_logo.png" />\n'
    html_string += "          </a>\n"
    html_string += "        </div>\n"
    html_string += "      </div>\n"
    html_string += '      <div class="player">\n'
    html_string += '        <a href="https://colonist.io/profile/' + opponent + '">\n'
    html_string += (
        '          <img class="player_img" src="catan/' + opponent + '.jpg" />\n'
    )
    html_string += "        </a>\n"
    html_string += "      </div>\n"
    html_string += '      <div class="wins_display">\n'
    html_string += '        <div class="big_container">\n'
    html_string += (
        '          <h1 class="big_wins" id="right">'
        + str(opponent_total_wins)
        + "</h1>\n"
    )
    html_string += (
        '          <h2 class="big_percent">('
        + str(round(opponent_total_wins / all_time_matches, 3))
        + ")</h2>\n"
    )
    html_string += "        </div>\n"
    html_string += "      </div>\n"
    html_string += "    </div>\n"
    html_string += '    <div class="tablediv">\n'
    html_string += '      <table class="data">\n'
    html_string += "        <tr>\n"
    html_string += "          <td>" + player + "</td>\n"
    html_string += "          <td>Player</td>\n"
    html_string += "          <td>" + opponent + "</td>\n"
    html_string += "        </tr>\n"
    html_string += "        <tr>\n"
    html_string += "          <td>" + str(player_total_wins) + "</td>\n"
    html_string += "          <td>Total Wins</td>\n"
    html_string += "          <td>" + str(opponent_total_wins) + "</td>\n"
    html_string += "        </tr>\n"
    html_string += "        <tr>\n"
    html_string += (
        "          <td>"
        + str(round(player_total_wins / all_time_matches, 3))
        + "</td>\n"
    )
    html_string += "          <td>Win Percentage</td>\n"
    html_string += (
        "          <td>"
        + str(round(opponent_total_wins / all_time_matches, 3))
        + "</td>\n"
    )
    html_string += "        </tr>\n"
    html_string += "        <tr>\n"
    html_string += "          <td>" + str(player_latest_date_wins) + "</td>\n"
    html_string += "          <td>Wins Today (" + latest_game_date + ")</td>\n"
    html_string += "          <td>" + str(opponent_latest_date_wins) + "</td>\n"
    html_string += "        </tr>\n"
    html_string += "      </table>\n"
    html_string += "    </div>\n"
    html_string += "  </body>\n"
    html_string += "</html>\n"

    return html_string


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
