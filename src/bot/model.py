from enum import Enum
from typing import NamedTuple
from typing import Optional

from praw.models.reddit.submission import Submission as RedditSubmission


class Judgement(Enum):
    YTA = "you're the asshole"
    NTA = "not the asshole"
    ESH = "everyone sucks here"
    NAH = "no assholes here"
    INFO = "not enough information"

    @staticmethod
    def from_reddit_link_flair_text(flair_text: str):
        flair_text = flair_text.lower()
        if flair_text == "Not the A-hole".lower():
            return Judgement.NTA

        elif flair_text == "No A-holes here".lower():
            return Judgement.NAH

        elif flair_text == "Asshole".lower():
            return Judgement.YTA

        elif flair_text == "Everyone Sucks".lower():
            return Judgement.ESH

        elif flair_text == "Not enough info".lower():
            return Judgement.INFO

        else:
            return None


class AITASubmission(NamedTuple):
    submission_id: str
    submission_title: str
    submission_body: str
    submitted_at_utc: float
    reddit_judgement: Optional[Judgement]
    annubis_judgement: Optional[Judgement]


def from_reddit_submission(
        reddit_submission: RedditSubmission,
        anubis_judgement: Optional[Judgement] = None
):
    return AITASubmission(
        submission_id=reddit_submission.id,
        submission_title=reddit_submission.title,
        submission_body=reddit_submission.selftext,
        submitted_at_utc=reddit_submission.created_utc,
        reddit_judgement=Judgement.from_reddit_link_flair_text(reddit_submission.link_flair_text),
        annubis_judgement=anubis_judgement
    )


def from_dict_submission(
        json_submission,
        anubis_judgement: Optional[Judgement] = None
):
    return AITASubmission(
        submission_id=json_submission["id"],
        submission_title=json_submission["title"],
        submission_body=json_submission["selftext"],
        submitted_at_utc=json_submission["created_utc"],
        reddit_judgement=Judgement.from_reddit_link_flair_text(json_submission["link_flair_text"]),
        annubis_judgement=anubis_judgement
    )
