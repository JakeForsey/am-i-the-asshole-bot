import argparse
import logging

from src.bot import config
from src.bot.ml import Anubis
from src.bot.data import AITASubmissionDAO
from src.bot.data import RedditScraper


CONFIG = config.get_config()
LOGGER = logging.getLogger(__name__)


def main(args):
    """
    Runs the in one of the modes.
    :return: None
    """

    dao = AITASubmissionDAO(
        CONFIG.integration.database.db_path
    )

    scraper = RedditScraper(
        client_id=CONFIG.integration.reddit.client_id,
        client_secret=CONFIG.integration.reddit.client_secret,
        user_agent=CONFIG.integration.reddit.user_agent
    )

    anubis = Anubis()

    if args.mode == "scrape":
        LOGGER.info("Scraping data for Anubis")

        for aita_submission in scraper.get_aita_submissions():
            dao.insert(aita_submission)

    elif args.mode == "train":
        LOGGER.info("Training Anubis")

        # TODO (Jake)  Write a training loop
        pass

    elif args.mode == "judge":
        LOGGER.info("Judging people with Anubis")

        for aita_submission in scraper.get_aita_submissions():
            judgement = anubis.judge(aita_submission)

            # TODO (Sam) Post the judgement on the submission with a witty comment


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--mode", choices=["scrape", "judge", "run"])
    argument_parser.add_argument("--logging_level", default=logging.DEBUG)

    args = argument_parser.parse_args()

    logging.basicConfig(level=args.logging_level)

    LOGGER.info("Running AITA Bot")
    LOGGER.info("Config: %s", CONFIG)
    LOGGER.info("Arguments: %s", args)

    main(args)
