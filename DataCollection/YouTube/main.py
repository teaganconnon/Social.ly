#controller to extract sponsored videos from keywords
import logging
from datetime import datetime

import pandas as pd

from yt import config, YouTube
from yt.logger import setup_logging

_LOGGER = logging.getLogger(__name__)

def main():
    _LOGGER.info('Starting sponsor search')
    start = datetime.now()
    dataset_version = start.strftime('%Y_%m_%d-%H:%M-%p')

    youtube = YouTube(
        url=config.URL,
        api_key=config.API_KEYS[0]
    )

    return

if __name__ == '__main__':
    setup_logging(config.LOG_LEVEL)