import logging
import random
from typing import List

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

from src.bot.model import Judgement
from src.bot.model import AITASubmission


LOGGER = logging.getLogger(__name__)


class Anubis:
    # TODO (Jake) Make this thing judge AITA submissions intelligently!
    def __init__(
            self,
            train_proportion=0.7
    ):
        self._train_proportion = train_proportion

        self._pipeline = Pipeline(
            steps=[
                ("vectorize", TfidfVectorizer(stop_words='english', ngram_range=(1, 3), max_df=0.3, min_df=3)),
                ("classify", GradientBoostingClassifier(
                    n_estimators=1000, verbose=True, subsample=0.8
                ))
            ]
        )

    def judge(self, submission: AITASubmission) -> Judgement:
        return Judgement.ESH

    def train(
            self,
            aita_submissions: List[AITASubmission]
    ):
        # Filter submissions that do not have a reddit judgement yet
        aita_submissions = [s for s in aita_submissions if s.reddit_judgement]
        sample_count = len(aita_submissions)
        LOGGER.info("Training and testing Anubis on %s samples", sample_count)

        train_sample_count = round(self._train_proportion * sample_count)
        LOGGER.info("Training Anubis on %s samples", train_sample_count)

        random.shuffle(aita_submissions)
        train, test = aita_submissions[: train_sample_count], aita_submissions[train_sample_count:]

        LOGGER.info("Fitting Anubis pipeline")
        self._pipeline.fit(
            [s.submission_body for s in train if s.reddit_judgement],
            [s.reddit_judgement for s in train if s.reddit_judgement]
        )

        LOGGER.info("Running Anubis on the test samples")
        predicted_judgements = self._pipeline.predict(
            [s.submission_body for s in test if s.reddit_judgement],
        )

        LOGGER.info("Producing classification report")

        print(classification_report(
            [s.reddit_judgement for s in test if s.reddit_judgement],
            predicted_judgements
        ))
