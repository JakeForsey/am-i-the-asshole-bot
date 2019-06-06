from abc import ABCMeta, abstractmethod

import logging
import random
from typing import List
from typing import Tuple

from fastai.text import TextLMDataBunch
from fastai.text import TextClasDataBunch
from fastai.text import language_model_learner
from fastai.text import AWD_LSTM
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

from src.bot.model import Judgement
from src.bot.model import AITASubmission


LOGGER = logging.getLogger(__name__)


class BaseModel(metaclass=ABCMeta):

    def __init__(self, train_proportion=0.7):
        self._train_proportion = train_proportion

    @abstractmethod
    def judge(self, submission: AITASubmission) -> Judgement:
        pass

    @abstractmethod
    def train(
            self,
            aita_submissions: List[AITASubmission]
    ):
        pass

    def train_test_split(
            self,
            aita_submissions: List[AITASubmission]
    ) -> Tuple[List[AITASubmission], List[AITASubmission]]:

        LOGGER.info("Spliting %s samples into train test datasets", len(aita_submissions))

        # Filter submissions that do not have a reddit judgement yet
        aita_submissions = [s for s in aita_submissions if s.reddit_judgement]

        # Work out how many training samples there will be
        sample_count = len(aita_submissions)
        train_sample_count = round(self._train_proportion * sample_count)

        # Split submissions into two lists
        random.shuffle(aita_submissions)
        train, test = aita_submissions[: train_sample_count], aita_submissions[train_sample_count:]

        LOGGER.info("Training samples %s", len(train))
        LOGGER.info("Testing samples %s", len(test))

        return train, test


class Anubis:
    @staticmethod
    def summon(model, *args, **kwargs) -> BaseModel:
        if model == "GradientBoosting":
            return GradientBoosting(*args, **kwargs)
        elif model == "AWDLSTM":
            return AWDLSTM(*args, **kwargs)
        else:
            LOGGER.error("Model not recognised: %", model)


class AWDLSTM(BaseModel):

    def __init__(self, tmp_data_path="tmp.csv", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tmp_data_path = tmp_data_path

    def judge(self, submission: AITASubmission):
        pass

    def train(
            self,
            aita_submissions: List[AITASubmission]
    ):
        train, test = self.train_test_split(aita_submissions)

        train_df = pd.DataFrame(train)
        test_df = pd.DataFrame(test)

        lm_data = TextLMDataBunch.from_df(
            self._tmp_data_path,
            train_df=train_df,
            valid_df=test_df,
            text_cols="submission_body"
        )

        clf_data = TextClasDataBunch.from_df(
            self._tmp_data_path,
            train_df=train_df,
            valid_df=test_df,
            vocab=lm_data.train_ds.vocab,
            text_cols="submission_body"
        )

        learner = language_model_learner(
            lm_data, AWD_LSTM
        )
        learner.unfreeze()
        results = learner.fit_one_cycle(4, slice(1e-2), moms=(0.8, 0.7))
        print(results)


class GradientBoosting(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pipeline = Pipeline(
            steps=[
                ("vectorize", TfidfVectorizer(stop_words='english', ngram_range=(1, 3), max_df=0.3, min_df=3)),
                ("classify", GradientBoostingClassifier(
                    n_estimators=100, verbose=True, subsample=0.8
                ))
            ]
        )

    def judge(self, submission: AITASubmission) -> Judgement:
        self._pipeline.predict(submission)

    def train(
            self,
            aita_submissions: List[AITASubmission]
    ):
        train, test = self.train_test_split(aita_submissions)

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
