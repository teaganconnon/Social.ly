# Code used from https://github.com/syahrulhamdani/ytid-trends/blob/main/common/video.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Video:
    #Video response instance
    id: str
    snippet: Dict[str, str]
    content_detail: Dict[str, Any]
    statistic: Dict[str, int]

    def get_id(self):
        return self.id

    def to_dict(self, **kwargs):
        #convert video response to dictionary
        content = {}
        statistic = {}

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
        if self.content_detail:
            content = {
                "duration": self.content_detail.get("duration"),
                "dimension": self.content_detail.get("dimension"),
                "definition": self.content_detail.get(
                    "definition"),
                "caption": self.content_detail.get("caption"),
                "license_status": self.content_detail.get(
                    "licensedContent"),
                "allowed_region": self.content_detail.get(
                    "regionRestriction", {}).get("allowed"),
                "blocked_region": self.content_detail.get(
                    "regionRestriction", {}).get("blocked"),
            }
        if self.statistic:
            statistic = {
                "view": self.statistic.get("viewCount"),
                "like": self.statistic.get("likeCount"),
                "favorite": self.statistic.get("favoriteCount"),
                "comment": self.statistic.get("commentCount")
            }
        video_id = {"video_id": self.id}

        return dict(**video_id, **snippet, **content, **statistic, **kwargs)