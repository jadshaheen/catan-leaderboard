import re
import sys

"""
If we ever modify jadshaheen.com/catan.html, we can run this script on the new file 
and copy the output to util.py's `build_html_string` method.
"""

"""
Line 11 match 2023-03-03 11:30:02 replace update_time
Line 15 match multi-digit integer replace str(player_total_wins)
Line 16 match up to 3-digit decimal .xxx, replace str(round(player_total_wins / all_time_matches, 3))
Line 27 match multi-digit integer, replace str(all_time_matches)
Line 42 match multi-digit integer, replace str(opponent_total_wins)
Line 43 match up to 3-digit decimal .xxx, replace str(round(opponent_total_wins / all_time_matches, 3))
Line 55 match MDI, replace str(player_total_wins)
Line 57 match MDI, replace str(opponent_total_wins)
Line 60 match up to 3-digit decimal .xxx, replace str(round(player_total_wins / all_time_matches, 3))
Line 62 match up to 3-digit decimal .xxx, replace str(round(opponent_total_wins / all_time_matches, 3))
Line 65 match SINGLE DIGIT INTEGER or more, replace str(player_latest_date_wins)
Line 66 match 2023-03-02, replace latest_game_date
Line 67 match SINGLE DIGIT INTEGER or more, replace str(opponent_latest_date_wins)

MULTI-DIGIT INTEGER: re.sub(r'\d\d+', "' + str(opponent_wins) + '", x)
DATE WITH TIME: re.sub(r'\d+-\d+-\d+ \d+:\d+:\d+', "' + update_time + '", x)
DATE WITHOUT TIME: re.sub(r'\d+-\d+-\d+', "' + latest_game_date + '", x)
DECIMAL: re.sub(r'\.\d+', "' + str(round(player_total_wins / all_time_matches, 3)) + '", x)
SDI+: re.sub(r'\d+', "' + str(player_latest_date_wins) + '", x)

"""

if __name__ == "__main__":
    filepath = "/Users/jad/Desktop/projects/jadshaheen.github.io/catan.html"
    try:
        filepath = sys.argv[1]
    except IndexError:
        pass

    method_opening = ""
    with open(filepath, "r") as file:
        lines = file.readlines()

    lines = ["html_string += '" + line.strip("\n") + "\\n'\n" for line in lines]
    lines[10] = re.sub(r"\d+-\d+-\d+ \d+:\d+:\d+", "' + update_time + '", lines[10])
    lines[14] = re.sub(r"\d\d+", "' + str(player_total_wins) + '", lines[14])
    lines[15] = re.sub(
        r"0\.\d+",
        "' + str(round(player_total_wins / all_time_matches, 3)) + '",
        lines[15],
    )
    lines[26] = re.sub(r"\d\d+", "' + str(all_time_matches) + '", lines[26])
    lines[41] = re.sub(r"\d\d+", "' + str(opponent_total_wins) + '", lines[41])
    lines[42] = re.sub(
        r"0\.\d+",
        "' + str(round(opponent_total_wins / all_time_matches, 3)) + '",
        lines[42],
    )
    lines[54] = re.sub(r"\d\d+", "' + str(player_total_wins) + '", lines[54])
    lines[56] = re.sub(r"\d\d+", "' + str(opponent_total_wins) + '", lines[56])
    lines[59] = re.sub(
        r"0\.\d+",
        "' + str(round(player_total_wins / all_time_matches, 3)) + '",
        lines[59],
    )
    lines[61] = re.sub(
        r"0\.\d+",
        "' + str(round(opponent_total_wins / all_time_matches, 3)) + '",
        lines[61],
    )
    lines[64] = re.sub(r"\d+", "' + str(player_latest_date_wins) + '", lines[64])
    lines[65] = re.sub(r"\d+-\d+-\d+", "' + latest_game_date + '", lines[65])
    lines[66] = re.sub(r"\d+", "' + str(opponent_latest_date_wins) + '", lines[66])

    print("".join(lines))
