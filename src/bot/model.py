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

        if flair_text == "Not the A-hole":
            return Judgement.NTA

        elif flair_text == "No A-holes here":
            return Judgement.NAH

        elif flair_text == "Asshole":
            return Judgement.YTA

        elif flair_text == "Everyone Sucks":
            return Judgement.ESH

        elif flair_text == "Not enough info":
            return Judgement.INFO

        else:
            return None


class AITASubmission(NamedTuple):
    submission_id: str
    submission_title: str
    submission_body: str
    submitted_at: float
    reddit_judgement: Optional[Judgement]
    annubis_judgement: Optional[Judgement]

    @staticmethod
    def from_reddit_submission(
            reddit_submission: RedditSubmission,
            anubis_judgement: Optional[Judgement] = None
    ):
        return AITASubmission(
            submission_id=reddit_submission.id,
            submission_title=reddit_submission.title,
            submission_body=reddit_submission.selftext,
            submitted_at=reddit_submission.created_utc,
            reddit_judgement=Judgement.from_reddit_link_flair_text(reddit_submission.link_flair_text),
            annubis_judgement=anubis_judgement
        )
