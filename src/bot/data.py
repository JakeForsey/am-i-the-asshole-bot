from typing import Iterable
from typing import List

import praw

from src.bot.model import Judgement
from src.bot.model import AITASubmission


class RedditScraper:

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            user_agent: str
    ):
        self._reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def get_submissions(self) -> Iterable[AITASubmission]:
        for submission in self._reddit.subreddit('AmItheAsshole').hot(limit=100):
            # If its a meta (submissions about the subreddit) submission then it
            # is not of interest
            if submission.link_flair_text == "META":
                continue

            yield AITASubmission.from_reddit_submission(submission)

    def get_judgement(self, submission_id: str) -> Judgement:
        # TODO get the flair for the submission (which will
        #   be added a few days after the submission is made)
        #   and convert it to a Judgement
        return Judgement.ESH


class SubmissionDAO:

    def __init__(self):
        pass

    def insert(self, submission: AITASubmission):
        pass

    def submissions(self) -> List[AITASubmission]:
        return [AITASubmission()]

    def submission_by_id(self, submission_id: str) -> AITASubmission:
        return AITASubmission()
