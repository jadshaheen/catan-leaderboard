import sys

"""
If we ever modify jadshaheen.com/catan.html, we can run this script on the new file 
and copy the output to colonist_history_scraper.py's `build_html_string` method.

TODO: Replace certain values with the method arguments injected into the strings
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
    print("".join(lines))
