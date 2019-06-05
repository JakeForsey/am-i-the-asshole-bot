from datetime import datetime
from enum import Enum
from typing import Optional

from praw.models.reddit.submission import Submission as RedditSubmission
from praw.models.reddit.submission import SubmissionFlair as RedditFlair


class Judgement(Enum):
    YTA = "you're the asshole"
    NTA = "not the asshole"
    ESH = "everyone sucks here"
    NAH = "no assholes here"
    NEI = "not enough information"

    def from_reddit_flair(self, reddit_flair: RedditFlair):
        print(reddit_flair)
        print(dir(reddit_flair))

        return Judgement()


class AITASubmission(Enum):
    submission_title: str
    submission_body: str
    submitted_at: datetime
    reddit_judgement: Optional[Judgement]
    anubis_judgement: Optional[Judgement]

    @staticmethod
    def from_reddit_submission(
            reddit_submission: RedditSubmission,
            anubis_judgement: Optional[Judgement] = None
    ):
        return AITASubmission(
            submission_title=reddit_submission.title,
            submission_body=reddit_submission.selftext,
            submitted_at=reddit_submission.date,
            reddit_judgement=Judgement.from_reddit_flair(reddit_submission.flair),
            annubis_judgement=anubis_judgement
        )
