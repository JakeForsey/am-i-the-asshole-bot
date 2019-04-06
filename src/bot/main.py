import argparse
import logging

from src.bot.model import Anubis
from src.bot import config


CONFIG = config.get_config()
LOGGER = logging.getLogger(__name__)


def main():
    """
    Runs the bot.
    :return: None
    """

    # TODO (Sam) Write a loop that checks for AITA submissions

    # TODO (Sam) Pass AITA submission to Anubis to receive a judgement!
    anubis = Anubis()
    # judgment = anubis.judge(aita_submission)

    # TODO (Sam) Post the judgementon the submission with a witty comment


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--example_arg")

    args = argument_parser.parse_args()

    main()
