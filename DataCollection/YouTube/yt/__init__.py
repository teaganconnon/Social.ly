#Code modified from https://github.com/syahrulhamdani/ytid-trends/blob/main/ytid/__init__.py
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import requests
from requests.exceptions import RequestException   

from video.video import Video
from channel.channel import Channel


_LOGGER = logging.getLogger(__name__)

@dataclass
class YouTube:
    # to use for searching, url=https://www.googleapis.com/youtube/v3/search
    # to use for getting video details, url=https://www.googleapis.com/youtube/v3/videos
    # api_key: API Key for app 
    
    api_keys: List[str]
    credential: int

    def _get(self, endpoint, params: Dict[str, Any]):
        try:
            res = requests.get(endpoint, params=params)
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

        cursor = None

        for i in range(num_pages):
            if cursor:
                params['pageToken'] = cursor

            try:
                response = self._get(endpoint='https://www.googleapis.com/youtube/v3/search', params=params)
            except RequestException as e:
                if e.response.reason_code == 'quotaExceeded':
                    self.credential += 1
                    if self.credential == 3: #magic number of api keys I have
                        raise Exception("Out of API Keys!")
                    params['key'] = self.api_keys[self.credential]
                    raise e
            else:
                videos.extend(response.get('items'))
                cursor = response.get('nextPageToken')

        videos = [
            Video(
                id=video.get("id").get('videoId'),
                snippet=video.get("snippet"),
                content_detail=video.get("contentDetails"),
                statistic=video.get("statistics"),
            )
            for video in videos
        ]

        return videos

    def get_video_from_id(self, video_id):
        params = {
            'key': self.api_keys[self.credential],
            'part': 'snippet,statistics,contentDetails,topicDetails',
            'id': video_id,
        }

        try:
            response = self._get(endpoint='https://www.googleapis.com/youtube/v3/videos', params=params)
        except RequestException as e:
            if e.response.reason_code == 'quotaExceeded':
                self.credential += 1
                if self.credential == 3: #magic number of api keys I have
                    raise Exception("Out of API Keys!")
                params['key'] = self.api_keys[self.credential]
                raise e
        else:
            video = response.get('items')[0]
            return Video(
                id=video.get("id"),
                snippet=video.get("snippet"),
                content_detail=video.get("contentDetails"),
                statistic=video.get("statistics"),
            )

    def get_channel_details(self, 
        channel_title: str = '',
        channel_id: str = ''):

        #stub method

        return
