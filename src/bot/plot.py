import logging
import sqlite3

LOGGER = logging.getLogger(__name__)


class Plotter:
    def __init__(self, dao):
        self._dao = dao

    def visualise_data(self):
        LOGGER.info('please work')
        return self

