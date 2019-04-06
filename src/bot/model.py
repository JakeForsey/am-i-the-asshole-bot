from enum import Enum


class Judgment(Enum):
    YTA = "you're the asshole"
    NTA = "not the asshole"
    ESH = "everyone sucks here"
    NAH = "no assholes here"
    NEI = "not enough information"


class Anubis:
    # TODO (Jake) Make this thing judge AITA submissions intelligently!
    def __init__(self):
        pass

    def judge(self, aita_submission: str) -> Judgment:
        return Judgment.ESH