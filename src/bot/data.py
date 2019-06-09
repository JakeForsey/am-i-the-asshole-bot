import logging
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Tuple

import pandas as pd
import praw
import sqlite3

from src.bot.model import Judgement
from src.bot.model import AITASubmission
from src.bot.model import from_reddit_submission
from src.bot.model import from_dict_submission


LOGGER = logging.getLogger(__name__)


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

    def get_pushshift_aita_submissions(self, urls: List[str]) -> Iterator[AITASubmission]:
        """
        Downloads data from http://files.pushshift.io/reddit/submissions/ and
        converts it into AITASubmissions.

        :param urls: A list of urls to scrape or a list of file paths
        :return: yields AITASubmissions
        """
        processed_submissions = 0
        processed_aita_submissions = 0

        for url_i, url in enumerate(urls):
            LOGGER.info("Processing url (%s / %s) %s ", url_i + 1, len(urls), url)

            try:
                LOGGER.debug("Initialising a generator for")

                # Create a generator that yields a few submissions at a time
                # pandas handles decompression by itself.
                submission_iterator = pd.read_json(
                    url,
                    lines=True, chunksize=1000,
                    dtype={
                        "id": str,
                        "title": str,
                        "selftext": str,
                        "link_flair_text": str,
                        "submitted_at": float
                    }
                )
                LOGGER.debug("Iterating over submissions")
                for chunk in submission_iterator:
                    for submission_row in chunk.to_dict(orient='records'):
                        if processed_submissions % 20 == 0:
                            LOGGER.info("Processed: %s reddit submissions", processed_submissions)
                            LOGGER.info("Processed: %s aita submissions", processed_aita_submissions)

                        if submission_row.get("subreddit", "") != "AmItheAsshole":
                            processed_submissions += 1
                            continue

                        processed_aita_submissions += 1
                        if submission_row["link_flair_text"] == "META":
                            continue

                        yield from_dict_submission(submission_row)

            except Exception as e:
                LOGGER.error("Failed to process something in %s", url, exc_info=e)

    def get_praw_submissions(self) -> Iterable[AITASubmission]:
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
