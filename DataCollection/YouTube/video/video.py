# Code used from https://github.com/syahrulhamdani/ytid-trends/blob/main/common/video.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Video:
    #Video response instance
    id: str
    snippet: Dict[str, str]
    content_details: Dict[str, Any]
    statistics: Dict[str, int]

    def get_id(self):
        return self.id

    def to_dict(self, **kwargs):
        #convert video response to dictionary
        snippet = {}
        content_details = {}
        statistics = {}

        video_id = {"video_id": self.id}
        
        if self.snippet:
            snippet = {
                "publish_time": self.snippet.get("publishedAt"),
                "channel_id": self.snippet.get("channelId"),
                "title": self.snippet.get("title"),
                "description": self.snippet.get("description"),
                # "thumbnail_url": self.snippet.get(
                #     "thumbnails", {}).get("high").get("url"),
                # "thumbnail_width": self.snippet.get(
                #     "thumbnails", {}).get("high").get("width"),
                # "thumbnail_height": self.snippet.get(
                #     "thumbnails", {}).get("high").get("height"),
                "channel_name": self.snippet.get("channelTitle"),
                "tags": self.snippet.get("tags"),
                "category_id": self.snippet.get("categoryId"),
                "live_status": self.snippet.get(
                    "liveBroadcastContent"),
                # "local_title": self.snippet.get(
                #     "localized", {}).get("title"),
                # "local_description": self.snippet.get(
                #     "localized", {}).get("description"),
            }
        if self.content_details:
            content_details = {
                "duration": self.content_details.get("duration"),
                "dimension": self.content_details.get("dimension"),
                "definition": self.content_details.get(
                    "definition"),
                "caption": self.content_details.get("caption"),
                "license_status": self.content_details.get(
                    "licensedContent"),
                "allowed_region": self.content_details.get(
                    "regionRestriction", {}).get("allowed"),
                "blocked_region": self.content_details.get(
                    "regionRestriction", {}).get("blocked"),
            }
        if self.statistics:
            statistics = {
                "views": self.statistics.get("viewCount"),
                "likes": self.statistics.get("likeCount"),
                "favorite": self.statistics.get("favoriteCount"),
                "comment": self.statistics.get("commentCount")
            }

        return dict(**video_id, **snippet, **content_details, **statistics, **kwargs)