import argparse
import logging
from pathlib import Path

from src.bot import config
from src.bot.ml import Anubis
from src.bot.data import AITASubmissionDAO
from src.bot.data import RedditScraper
from src.bot.cache import FileURLCache


CONFIG = config.get_config()
LOGGER = logging.getLogger(__name__)
ROOT_DIR = Path().resolve().parent.parent


def main(args):
    """
    Runs the in one of the modes.
    :return: None
    """

    dao = AITASubmissionDAO(
        Path(Path.resolve().parent.parent, "data", CONFIG.integration.database.db_path)
    )

    scraper = RedditScraper(
        client_id=CONFIG.integration.reddit.client_id,
        client_secret=CONFIG.integration.reddit.client_secret,
        user_agent=CONFIG.integration.reddit.user_agent
    )

    anubis = Anubis.summon(
        "AWDLSTM",
        train_proportion=0.7,
        tmp_data_path=Path(ROOT_DIR, "data", "awd_lstm")
    )

    if args.mode == "scrape":
        LOGGER.info("Scraping data for Anubis")

        if CONFIG.sources.pushshift.enabled:
            LOGGER.info("Scraping data for Anubis from http://files.pushshift.io/reddit")

            for aita_submission in scraper.get_pushshift_aita_submissions(
                    FileURLCache(Path(ROOT_DIR, "data", "pushshift"), CONFIG.sources.pushshift.urls)
            ):
                dao.insert(aita_submission)

        if CONFIG.sources.praw.enabled:
            LOGGER.info("Scraping data for Anubis from the praw Reddit API")
            for aita_submission in scraper.get_praw_submissions():
                dao.insert(aita_submission)

    elif args.mode == "update":
        LOGGER.info("Updating Reddit judgements")
        aita_submissions = dao.aita_submissions(where_clause="WHERE reddit_judgement is NULL")

        for aita_submission in aita_submissions:
            judgement = scraper.get_judgement(aita_submission.submission_id)

            if judgement:
                aita_submission = aita_submission._replace(reddit_judgement=judgement)
                dao.update_reddit_judgment(aita_submission)

    elif args.mode == "train":
        LOGGER.info("Training Anubis")

        anubis.train(
            list(dao.aita_submissions()),
            limit=None
        )

    elif args.mode == "judge":
        LOGGER.info("Judging people with Anubis")

        for aita_submission in scraper.get_praw_submissions():
            judgement = anubis.judge(aita_submission)

            # TODO (Sam) Post the judgement on the submission with a witty comment


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--mode", choices=["scrape", "train", "judge", "update"])
    argument_parser.add_argument("--logging_level", default=logging.DEBUG)

    args = argument_parser.parse_args()

    logging.basicConfig(level=args.logging_level)

    LOGGER.info("Running AITA Bot")
    LOGGER.info("Config: %s", CONFIG)
    LOGGER.info("Arguments: %s", args)

    main(args)
