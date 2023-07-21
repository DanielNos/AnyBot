from typing import Dict
import os, json
from collections import namedtuple


Poll = namedtuple("Poll", ["emojis", "can_change_votes", "voted"])


def progress_bar(value: float = 0, max: float = 0) -> str:
    if max == 0 or value == 0:
        return "`" + (" " * 30)  +"` | 0% (0)"

    percentage = round((value / max) * 30)

    bar = "`" + ("█" * percentage) + (" " * (30 - percentage)) + "`"

    bar += " | " + str(round((value / max) * 1000) / 10) + "% (" + str(value) + ")"

    return bar


def check_files():
    # Check if directory, file exists
    if not os.path.exists("./modules_data/polls/"):
        os.mkdir("./modules_data/polls")

    if not os.path.exists("./modules_data/polls/polls"):
        with open("./modules_data/polls/polls", "x") as file:
            file.write("{}")

        return False
    
    return True


def save_polls(polls: Dict):
    check_files()

    # Write data
    with open("./modules_data/polls/polls", "w") as file:
        file.write(json.dumps(polls, indent=4))


def save_poll(id: int, poll: Poll):
    check_files()

    # Load data
    with open("./modules_data/polls/polls", "r") as file:
        json_obj = json.load(file)

    # Insert poll
    json_obj[str(id)] = [poll.emojis, poll.can_change_votes, poll.voted]

    with open("./modules_data/polls/polls", "w") as file:
        file.write(json.dumps(json_obj, indent=4))


def load_polls() -> Dict[int, Poll]:
    if not check_files():
        return {}
    
    # Load data
    with open("./modules_data/polls/polls", "r") as file:
        json_obj = json.load(file)

    # Convert keys from strings to ints
    polls = {}
    for key in json_obj:
        polls[int(key)] = Poll(json_obj[key][0], json_obj[key][1], json_obj[key][2])

    return polls