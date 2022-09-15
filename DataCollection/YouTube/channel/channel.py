from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class Channel:
    #Channel response instance
    id: str
    snippet: Dict[str, Any]
    content_details: Dict[str, Any]
    statistics: Dict[str, Any]
    branding_settings: Dict[str, str]
    topic_details: Dict[str, List]
    branding_settings: Dict[str, str]

    def to_dict(self, **kwargs):
        #convert channel response to dictionary

        channel_id = {"channel_id": self.id}
        snippet = {
            "title": self.snippet.get("title"),
            "description": self.snippet.get("description"),
            "custom_url": self.snippet.get("customUrl"),
            "publish_time": self.snippet.get("publishedAt"),
            "thumbnail_url": self.snippet.get(
                "thumbnails", {}).get("high").get("url"),
            "thumbnail_width": self.snippet.get(
                "thumbnails", {}).get("high").get("width"),
            "thumbnail_height": self.snippet.get(
                "thumbnails", {}).get("high").get("height"),
            "default_language": self.snippet.get("defaultLanguage"),
            "local_title": self.snippet.get(
                "localized", {}).get("title"),
            "local_description": self.snippet.get(
                "localized", {}).get("description"),
            "country": self.snippet.get("country"),
        }
        content = {
            "likes": self.snippet.get(
                "relatedPlaylists", {}).get("likes"),
            "favorites": self.snippet.get(
                "relatedPlaylists", {}).get("uploads"),
        }
        statistics = {
            "views": self.statistics.get("viewCount"),
            "subscribers": self.statistics.get("subscriberCount"),
            "hidden_subscriber_count": self.statistics.get("hiddenSubscriberCount"),
            "video_count": self.statistics.get("videoCount"),
        }
        topic_details = {
            "topic_categories": self.topic_details.get("topicCategories")
        }
        branding_settings = {
            "keywords": self.branding_settings.get(
                "channel", {}).get("keywords"),
            "tracking_analytics_account_id": self.branding_settings.get(
                "channel", {}).get("trackingAnalyticsAccountId"),
        }

        return dict(**channel_id, **snippet, **content, **statistics, **topic_details, **branding_settings, **kwargs)