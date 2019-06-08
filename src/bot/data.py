from typing import Iterable
from typing import Iterator
from typing import List
from typing import TextIO
from typing import Tuple
from typing import Union

import json
import praw
import sqlite3

from src.bot.model import Judgement
from src.bot.model import AITASubmission
from src.bot.model import from_reddit_submission
from src.bot.model import from_dict_submission


class RedditParser:
    """Parses data from http://files.pushshift.io/reddit/ into AITASubmissions"""
    def __init__(self):
        pass

    def parse(self, file: Union[str, TextIO]) -> Iterator[AITASubmission]:
        if isinstance(file, str):
            file = open(file, "r")

        for line in file:
            submission_dict = json.loads(line)
            if submission_dict.get("subreddit", "") == "AmItheAsshole":
                print(submission_dict)
                yield from_dict_submission(submission_dict)


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

    def get_aita_submissions(self) -> Iterable[AITASubmission]:
        flair_texts = []
        for period in ["all", "year", "month", "week", "day"]:
            for submission in self._reddit.subreddit('AmItheAsshole').top(period, limit=10000000):

                flair_texts.append(submission.link_flair_text)

                # If its a meta (submissions about the subreddit) submission then it
                # is not of interest
                if submission.link_flair_text == "META":
                    continue

                yield from_reddit_submission(submission)

    def get_judgement(self, submission_id: str) -> Judgement:
        # TODO get the flair for the submission (which will
        #   be added 18 hours after the submission is made)
        #   and convert it to a Judgement
        return Judgement.ESH


class AITASubmissionDAO:

    INITIALISE_DB_SQL = """
    CREATE TABLE IF NOT EXISTS aita_submission(
        submission_id text PRIMARY KEY,
        submission_title text,
        submission_body text,
        submitted_at_utc real,
        reddit_judgement text,
        annubis_judgement text
    );
    """

    INSERT_SUBMISSION_SQL = """
    INSERT OR IGNORE INTO aita_submission(
        submission_id,
        submission_title,
        submission_body,
        submitted_at_utc,
        reddit_judgement,
        annubis_judgement
    ) VALUES (?, ?, ?, ?, ?, ?)
    """

    def __init__(self, db_path):
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row

        cursor = self._conn.cursor()
        cursor.execute(self.INITIALISE_DB_SQL)

    def insert(self, aita_submission: AITASubmission):
        cursor = self._conn.cursor()
        cursor.execute(
            self.INSERT_SUBMISSION_SQL,
            self.aita_submission_to_record(aita_submission)
        )
        self._conn.commit()

    def aita_submissions(self) -> List[AITASubmission]:
        cursor = self._conn.cursor()
        for row in cursor.execute('SELECT * FROM aita_submission'):
            yield AITASubmission(
                **row
            )

    @staticmethod
    def aita_submission_to_record(aita_submission: AITASubmission) -> Tuple:
        if aita_submission.reddit_judgement:
            reddit_judgement_str = aita_submission.reddit_judgement.name
        else:
            reddit_judgement_str = None

        if aita_submission.annubis_judgement:
            anubis_judgement_str = aita_submission.annubis_judgement.name
        else:
            anubis_judgement_str = None

        return (
            aita_submission.submission_id,
            aita_submission.submission_title,
            aita_submission.submission_body,
            aita_submission.submitted_at_utc,
            reddit_judgement_str,
            anubis_judgement_str
        )
