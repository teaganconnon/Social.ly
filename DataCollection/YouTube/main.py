#controller to extract sponsored videos from keywords
import logging
from datetime import datetime
from time import time
from pathlib import Path

import pandas as pd

from common.utils import save_to_csv
from yt import config, YouTube
from yt.logger import setup_logging

_LOGGER = logging.getLogger(__name__)

SEARCH_TERMS = ['turtleneck']
NUM_PAGES = 1

def main():
    _LOGGER.info('Starting sponsor search')
    start = datetime.now()
    dataset_version = start.strftime('%Y_%m_%d-%H:%M-%p')

    youtube = YouTube(
        api_keys=config.API_KEYS,
        credential=0
    )

    search_results = []

    search_start = time()

    for search_term in SEARCH_TERMS:
        search_results.extend(youtube.search(search_term, NUM_PAGES)) # this doesn't return a full description so need to query api again

    search_results = [
        youtube.get_video_from_id(video.get_id())
        for video in search_results
    ]

    search_end = time()

    _LOGGER.debug(f"Retrieved {NUM_PAGES * 50 * len(SEARCH_TERMS)} results in {search_end - search_start}s")

    df_videos = pd.DataFrame([
        video.to_dict()
        for video in search_results
    ])

    _LOGGER.info(f"Retrieved {df_videos.shape[0]} total videos")

    print(df_videos.info())

    filename = Path(config.DATADIR) / f"search_results_{dataset_version}.csv"
    save_to_csv(df_videos, filename.as_posix())
    df_saved = pd.read_csv(filename)
    _LOGGER.info("Done saving %d trending videos (%s). Total videos: %d",
                 df_videos.shape[0], filename, df_saved.shape[0])


if __name__ == '__main__':
    setup_logging(config.LOG_LEVEL)
    main()