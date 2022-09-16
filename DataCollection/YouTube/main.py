#controller to extract sponsored videos from keywords
import logging
import re
from datetime import datetime
from time import time
from pathlib import Path

import pandas as pd

from common.utils import save_to_csv
from yt import config, YouTube
from yt.logger import setup_logging

_LOGGER = logging.getLogger(__name__)

#these consts are probably gonna be what the user gets to choose, although maybe just search terms and num-pages at end of day
SEARCH_TERMS = ['turtleneck']
KEYWORD_TERMS = ["sponsor", "use code", "sign up", "click the link", "use the link", "use my link", "click on the link", "brought to you by"]
FALSE_KEYWORDS = ["not sponsor", "not a sponsor", "no sponsor", "notsponsor", "isn't sponsored", "isnt sponsored"]

NUM_PAGES = 1
MAX_RESULTS = 50

def sponsor_search(search_terms, keyword_terms, false_keywords, num_pages: int = 3, max_results: int = 50, save_csv: bool = False):
    """
        Searches youtube using list of search terms
        Looks through video results descriptions for keyword term matches
        Eliminates false positive results
        Returns pandas dataframe of keyword term hits

        num_pages controls search depth per keyword
        max_results: int 0-50 determines results per page returned from youtube api
        save_csv: if True, a csv will be saved containing the info from the dataframe to the /data directory

        Sample Result dataframe.info():

        Data columns (total 20 columns):
        #   Column          Non-Null Count  Dtype 
       ---  ------          --------------  ----- 
        0   video_id        50 non-null     object
        1   publish_time    50 non-null     object
        2   channel_id      50 non-null     object
        3   title           50 non-null     object
        4   description     50 non-null     object
        5   channel_name    50 non-null     object
        6   tags            31 non-null     object
        7   category_id     50 non-null     object
        8   live_status     50 non-null     object
        9   duration        50 non-null     object
        10  dimension       50 non-null     object
        11  definition      50 non-null     object
        12  caption         50 non-null     object
        13  license_status  50 non-null     bool  
        14  allowed_region  3 non-null      object
        15  blocked_region  0 non-null      object
        16  views           50 non-null     object
        17  likes           48 non-null     object
        18  favorite        50 non-null     object
        19  comment         50 non-null     object
        dtypes: bool(1), object(19)

    """

    _LOGGER.info('Starting sponsor search')
    _LOGGER.info(f"This operation will use {(100 + max_results) * len(search_terms) * num_pages} API points")
    start = datetime.now()
    dataset_version = start.strftime('%Y_%m_%d-%H:%M-%p')

    youtube = YouTube(
        api_keys=config.API_KEYS,
        credential=0
    )

    search_results = []

    search_start = time()

    for search_term in search_terms:
        search_results.extend(youtube.search(search_term, num_pages)) # this doesn't return a full description so need to query api again, kind of a waste of the other stuff in the snippet smh

    #optimal api point usage would entail dropping duplicates here
    search_results = [*set(search_results)] # or i could extract all unique ids from search results but allegedly *set is fast

    search_results = [
        youtube.get_video_from_id(video.get_id())
        for video in search_results
    ]

    search_end = time()

    _LOGGER.debug(f"Retrieved {num_pages * 50 * len(search_terms)} results in {search_end - search_start}s")

    df_videos = pd.DataFrame([
        video.to_dict()
        for video in search_results
    ])

    _LOGGER.info(f"Retrieved {df_videos.shape[0]} total videos")

    # drop nonunique video ids
    df_videos.drop_duplicates(subset=['video_id'])
    # iterate through descriptions looking for substring matches from keyword search and add to new data frame
    keyword_string = "|".join(keyword_terms)
    sponsored_videos = df_videos.loc[df_videos['description'].str.contains(keyword_string, case=False)].copy()
    #add column containing keywords which hit
    sponsored_videos['keyword_hits'] = sponsored_videos['description'].str.findall(keyword_string, flags=re.IGNORECASE)
    # iterate through hits to look for false positives and drop those
    false_keyword_string = "|".join(false_keywords)
    sponsored_videos_cleaned = sponsored_videos.loc[~sponsored_videos['description'].str.contains(false_keyword_string)]
    # return dataframe

    if save_csv:
        filename = Path(config.DATADIR) / f"sponsored_videos_{dataset_version}.csv"
        save_to_csv(sponsored_videos_cleaned, filename.as_posix())
        df_saved = pd.read_csv(filename)
        _LOGGER.info("Done saving %d sponsored videos (%s). Total videos: %d",
                    sponsored_videos_cleaned.shape[0], filename, df_saved.shape[0])

    return sponsored_videos_cleaned


if __name__ == '__main__':
    setup_logging(config.LOG_LEVEL)
    sponsor_search(search_terms=SEARCH_TERMS, keyword_terms=KEYWORD_TERMS, false_keywords=FALSE_KEYWORDS, num_pages=NUM_PAGES, max_results=MAX_RESULTS, save_csv=True)