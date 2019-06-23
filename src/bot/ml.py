from abc import ABCMeta, abstractmethod
import logging
import random
from typing import List
from typing import Tuple
from typing import Optional

from fastai.text import AWD_LSTM
from fastai.text import ClassificationInterpretation
from fastai.text import language_model_learner
from fastai.text import TextLMDataBunch
from fastai.text import TextClasDataBunch
from fastai.text import text_classifier_learner
import matplotlib.pyplot as plt
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
    def _judge(self, submission: AITASubmission) -> Judgement:
        pass

    @abstractmethod
    def _train(
            self,
            train: List[AITASubmission],
            test: List[AITASubmission],
            valid: List[AITASubmission],
    ):
        pass

    def judge(self, submission: AITASubmission) -> Judgement:
        return self._judge(submission)

    def train(
            self,
            aita_submissions: List[AITASubmission],
            limit: Optional[int] = None,
            categories: Optional[List[Judgement]] = None
    ):
        # Filter down to specific categories
        if categories:
            aita_submissions = [
                s for s in aita_submissions
                if s.reddit_judgement in categories
            ]

        train, valid_test = self._split(aita_submissions, self._train_proportion)
        valid, test = self._split(valid_test, 0.5)

        if limit:
            train = train[:limit]
            test = test[:limit]
            valid = valid[:limit]

        return self._train(train, test, valid)

    def _split(
            self,
            aita_submissions: List[AITASubmission],
            proportion: float
    ) -> Tuple[List[AITASubmission], List[AITASubmission]]:

        # Filter submissions that do not have a reddit judgement yet
        aita_submissions = [s for s in aita_submissions if s.reddit_judgement]

        # Work out how many samples there will be
        sample_count = len(aita_submissions)
        train_sample_count = round(proportion * sample_count)

        # Split submissions into two lists
        random.shuffle(aita_submissions)
        train, test = aita_submissions[: train_sample_count], aita_submissions[train_sample_count:]

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

        self._model = None

    def _judge(self, submission: AITASubmission):
        self._model.predict(submission.submission_body)

    def _train(
            self,
            train: List[AITASubmission],
            test: List[AITASubmission],
            valid: List[AITASubmission],
    ):

        train_df = pd.DataFrame(train)
        valid_df = pd.DataFrame(valid)
        test_df = pd.DataFrame(test)

        LOGGER.info("Initialising data set for language modelling")
        lm_data = TextLMDataBunch.from_df(
            self._tmp_data_path,
            train_df=train_df,
            valid_df=valid_df,
            test_df=test_df,
            text_cols="submission_body",
            bs=32,
            min_freq=3,
        )
        LOGGER.info("Language model data bunch: %s", lm_data)

        LOGGER.info("Initialising data set for classification")
        clf_data = TextClasDataBunch.from_df(
            self._tmp_data_path,
            train_df=train_df,
            valid_df=valid_df,
            test_df=test_df,
            vocab=lm_data.train_ds.vocab,
            text_cols="submission_body",
            label_cols="reddit_judgement",
            bs=8
        )
        LOGGER.info("Classification data bunch: %s", clf_data)

        LOGGER.info("Vocabulary contains %s words", len(lm_data.train_ds.vocab.itos))

        LOGGER.info("Training language model encoder")
        # Fine tune the pretrained language model on the aita submissions
        learner = language_model_learner(lm_data, AWD_LSTM)
        learner.unfreeze()
        learner.fit_one_cycle(20)
        learner.save_encoder('enc')

        LOGGER.info("Training classifier")
        # Train a classifier using the fine tuned language model above
        # as an encoder
        learner = text_classifier_learner(clf_data, AWD_LSTM)
        learner.load_encoder('enc')
        learner.fit_one_cycle(20)
        learner.unfreeze()
        learner.fit_one_cycle(40)

        interp = ClassificationInterpretation.from_learner(learner)
        interp.plot_confusion_matrix(title='Confusion matrix')
        plt.show()

        self._model = learner

        LOGGER.info("Training complete")

        print(self._model.predict("""
        Wife and I got married as widowers. My late wife and daughter passed away in an accident. My daughter was only 1 when she passed away. My current wife had 3 yo twins when we got married. The girls are 15 now.

        So, yesterday when wife and I were watching a movie, she told me that the girls were planning a surprise for me on their birthday. And when I asked her what it was, she told me that they wanted me to adopt them. I was really happy, because it meant that I had done a good job, but unfortunately I cannot adopt them. I'm actually glad that my wife told me that. A surprise would have caught me off guard.
        
        The thing is, my wife and I had discussed about this when they were young. I made it clear that I didn't want to adopt anyone or have more children. Call it coping up with my daughter's death or whatever, but I've never felt comfortable thinking about it. My wife is now asking me to say yes.
        
        I've been there for them and I'll always be there for them. I love them but I don't think I'll be comfortable adopting them. WIBTA here?
        
        """))
        print(self._model.predict("""
        Friend visited me in Japan from US. She’s borderline obese. She’s been here for few weeks, I take her to interesting places, she gets some weird looks because of her weight. She noticed too. She said that it was because she’s white and looks different (I’m white too, there are lots of white people here and No one looks at them weirdly) I just agreed with it. Few days later she started getting frustrated, she asked why were people looking at her again and I said as politely as I could. “Don’t take this the wrong way, but there aren’t lots of chubby people here. As you noticed almost everyone is thin and sometimes people are surprised or caught off guard when they see a bigger person”

        She just went to her room without saying a word. She’s been acting weird and distant and we haven’t brought this talk up after that.
        """))


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

    def _judge(self, submission: AITASubmission) -> Judgement:
        self._pipeline.predict(submission)

    def _train(
            self,
            train: List[AITASubmission],
            test: List[AITASubmission],
            valid: List[AITASubmission],
    ):

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
