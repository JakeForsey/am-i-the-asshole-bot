from src.bot.config import get_config
from src.bot.data import RedditScraper
from src.bot.data import AITASubmissionDAO


def scape():
    cfg = get_config()

    scraper = RedditScraper(
        client_id=cfg.integration.reddit.client_id,
        client_secret=cfg.integration.reddit.client_secret,
        user_agent=cfg.integration.reddit.user_agent
    )

    dao = AITASubmissionDAO()

    for submission in scraper.get_aita_submissions():
        print(submission)
        dao.insert(submission)


if __name__ == "__main__":
    scape()
