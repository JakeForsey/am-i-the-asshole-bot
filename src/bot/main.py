import argparse
import logging

from src.bot import config
from src.bot.ml import Anubis
from src.bot.data import AITASubmissionDAO
from src.bot.data import RedditScraper
from src.bot.data import RedditParser


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
    parser = RedditParser()

    anubis = Anubis()

    if args.mode == "scrape":
        LOGGER.info("Scraping data for Anubis")

        # TODO (Jake or Sam) Make this run over and over on a schedule
        for aita_submission in scraper.get_aita_submissions():
            dao.insert(aita_submission)

    elif args.mode == "parse":
        LOGGER.info("Parsing data from file")
        for aita_submission in parser.parse(args.file):
            dao.insert(aita_submission)

    elif args.mode == "train":
        LOGGER.info("Training Anubis")

        anubis.train(
            list(dao.aita_submissions())
        )

    elif args.mode == "judge":
        LOGGER.info("Judging people with Anubis")

        for aita_submission in scraper.get_aita_submissions():
            judgement = anubis.judge(aita_submission)

            # TODO (Sam) Post the judgement on the submission with a witty comment


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--mode", choices=["scrape", "train", "judge", "parse"])
    argument_parser.add_argument("--logging_level", default=logging.DEBUG)
    argument_parser.add_argument("--file", help="File to be parsed by RedditParser")

    args = argument_parser.parse_args()

    logging.basicConfig(level=args.logging_level)

    LOGGER.info("Running AITA Bot")
    LOGGER.info("Config: %s", CONFIG)
    LOGGER.info("Arguments: %s", args)

    main(args)
