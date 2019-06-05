import praw

from src.bot.config import get_config
from src.bot.data import RedditScraper


def scape():
    cfg = get_config()

    scraper = RedditScraper(
        client_id=cfg.integration.reddit.client_id,
        client_secret=cfg.integration.reddit.client_secret,
        user_agent=cfg.integration.reddit.user_agent
    )

    for submission in scraper.get_submissions():
        print(submission)

        # TODO (Jake) Parse number of NTA YTA etc. and save to csv


if __name__ == "__main__":
    scape()
