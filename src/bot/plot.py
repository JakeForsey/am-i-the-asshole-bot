import logging
import sqlite3

LOGGER = logging.getLogger(__name__)

class plotter:

    def loadDB(self):
     LOGGER.info('load data')

     #1 load sqlite data
     #2 do some magic with it
     #3 plot with matplotlib :-)