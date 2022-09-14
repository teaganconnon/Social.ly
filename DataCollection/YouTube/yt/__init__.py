#Code modified from https://github.com/syahrulhamdani/ytid-trends/blob/main/ytid/__init__.py
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import requests
from requests.exceptions import RequestException   

from video.video import Video


_LOGGER = logging.getLogger(__name__)

@dataclass
class YouTube:
    # to use for searching, url=https://www.googleapis.com/youtube/v3/search
    # api_key: API Key for app
    # 
    
    api_keys: List[str]
    url: str
    credential: int

    def _get(self, params: Dict[str, Any]):
        try:
            res = requests.get(self.url, params=params)
            res.raise_for_status()
        except RequestException as e:
            raise e
        else:
            return res.json()

    def search(self, 
        search_term, 
        num_pages: int = 1,
        search_type: str = 'video',
        max_results: int = 50, 
        )-> List[Video]:

        params = {
            'key': self.api_keys[self.credential],
            'type': search_type,
            'part': 'snippet',
            'q': search_term,
            'maxResults': max_results,
        }

        videos = []

        for i in range(num_pages):
            if cursor:
                params['pageToken'] = cursor

            try:
                response = self._get(params)
            except RequestException as e:
                self.credential += 1
                if self.credential == 3: #magic number of api keys I have
                    raise Exception("Out of API Keys!")
                params['key'] = self.api_keys[self.credential]
            else:
                videos.extend(response.get('items'))
                cursor = response.get('nextPageToken')

        videos = [
            Video(
                id=video.get("id"),
                snippet=video.get("snippet"),
            )
            for video in videos
        ]

        return videos
