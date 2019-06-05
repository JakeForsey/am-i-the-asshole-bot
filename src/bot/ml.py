from src.bot.model import Judgement
from src.bot.model import AITASubmission


class Anubis:
    # TODO (Jake) Make this thing judge AITA submissions intelligently!
    def __init__(self):
        pass

    def judge(self, submission: AITASubmission) -> Judgement:
        return Judgement.ESH