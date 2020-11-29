import os
import logging


class Logger:
    def __init__(self, name, logFilePath):
        formatString = '%(asctime)s: [%(levelname)s]:[{}]: %(message)s'.format(
            name)
        logging.basicConfig(filename=logFilePath,
                            filemode='w', level=logging.INFO, format=formatString)

    def WriteDebug(self, msg):
        logging.debug(msg)

    def WriteInfo(self, msg):
        logging.info(msg)

    def WriteWarning(self, msg):
        logging.warning(msg)

    def WriteError(self, msg):
        logging.warning(msg)

    def WriteLog(self, msg, level):
        if level == 'debug':
            self.WriteDebug(msg)
        elif level == 'info':
            self.WriteInfo(msg)
        elif level == 'warning':
            self.WriteWarning(msg)
        elif level == 'error':
            self.WriteError(msg)
