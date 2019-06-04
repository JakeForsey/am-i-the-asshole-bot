import praw

from src.bot.config import get_config


def scape():
    cfg = get_config()

    reddit = praw.Reddit(
        client_id=cfg.integration.reddit.client_id,
        client_secret=cfg.integration.reddit.client_secret,
        user_agent=cfg.integration.reddit.user_agent
    )

    for submission in reddit.subreddit('AmItheAsshole').hot(limit=10):
        print(submission.title)
        print(submission.selftext)
        print(submission.comments)
        # TODO (Jake) Parse number of NTA YTA etc. and save to csv


if __name__ == "__main__":
    scape()
