from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import urllib.parse as p
import re
import os
import pickle
import string

from urllib.error import HTTPError

# api code comes from https://www.thepythoncode.com/article/using-youtube-api-in-python

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

#credentials = ["credentials.json", "credentials2.json", "credentials3.json"] #filenames of the OAuth credentials to bypass 10,000 point limit

punct_table = str.maketrans('', '', string.punctuation)

# api call functions

#this needs to be rewritten as a class probably but i don't know how classes work in python

def youtube_authenticate(credentials):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    if os.path.exists(f"env/{credentials}"):
        client_secrets_file = f"env/{credentials}"
    else:
        raise Exception("invalid credentials file / missing path")
    creds = None

    #if token already exists, use it
    if os.path.exists(f"env/{credentials}_token.pickle"):
        with open(f"env/{credentials}_token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: #if token exists but is expired, refresh
            creds.refresh(Request())
        else: #generate new token
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)

            with open(f"env/{credentials}_token.pickle", "wb") as token:
                pickle.dump(creds, token)

    return build(api_service_name, api_version, credentials=creds, cache_discovery=False)

def get_video_details(youtube, **kwargs):
    # return details by video id
    return youtube.videos().list(
        part="snippet,contentDetails,statistics",
        **kwargs
    ).execute()

def get_video_snippet(youtube, **kwargs):
    # return details by video id
    return youtube.videos().list(
        part="snippet", 
        **kwargs
    ).execute()

def search(youtube, **kwargs):
    # search by query for videos / channels/ playlists
    request = youtube.search().list(
        part="id,snippet",
        **kwargs
        )
    try:
        return request.execute()
    except HTTPError as e:
        # this is where the credential switch needs to happen / a signal needs to be passed up to whatever called this
        if e.reason == 'quotaExceeded':
            print(e)
            return e
        else:
            print(e)


def get_channel_videos(youtube, **kwargs):
    # search by channel id for associated videos
    return youtube.search().list(
        **kwargs
    ).execute()    

def get_channel_details(youtube, **kwargs):
    # get channel details by channel id
    return youtube.channels().list(
        part="statistics,snippet,contentDetails",
        **kwargs
    ).execute()

def get_comments(youtube, **kwargs):
    return youtube.commentThreads().list(
        part="snippet",
        **kwargs
    ).execute()

# helper functions

def parse_video_url(url):
    parsed_url = p.urlparse(url)

    video_id = p.parse_qs(parsed_url.query).get("v")
    if video_id:
        return video_id[0]
    else:
        raise Exception(f"Wasn't able to parse video URL: {url}")

def print_video_details(video_response):
    items = video_response.get("items")[0]
    snippet = items["snippet"]
    statistics = items["statistics"]
    content_details = items["contentDetails"]

    # print(items)
    # print(snippet)
    # print(statistics)
    # print(content_details)
    
    #details from snippet
    channel_title = snippet["channelTitle"]
    title = snippet["title"]
    description = snippet["description"]
    publish_time = snippet["publishedAt"]
    #details from statistics
    comment_count = statistics["commentCount"]
    like_count = statistics["likeCount"]
    view_count = statistics["viewCount"]
    #details from content details
    duration = content_details["duration"]

    # duration comes in in a weird format so this makes it human readable

    parsed_duration = re.search(f"PT(\d+H)?(\d+M)?(\d+S)", duration).groups()
    duration_str = ""
    for d in parsed_duration:
        if d:
            duration_str += f"{d[:-1]}:"
    duration_str = duration_str.strip(":")

    #final print format
    print(f"""\
    Title: {title}
    Description: {description}
    Channel Title: {channel_title}
    Publish time: {publish_time}
    Duration: {duration_str}
    Number of comments: {comment_count}
    Number of likes: {like_count}
    Number of views: {view_count}
    """)

def parse_channel_url(url):
    # checks url to see if it includes a channel ID, user ID, or channel name
    path = p.urlparse(url).path
    id = path.split("/")[-1]
    if "/c/" in path:
        return "c", id
    elif "/channel/" in path:
        return "channel", id
    elif "/user/" in path:
        return "user", id

def get_channel_id_by_url(youtube, url):
    """
    Returns channel ID of a given `id` and `method`
    - `method` (str): can be 'c', 'channel', 'user'
    - `id` (str): if method is 'c', then `id` is display name
        if method is 'channel', then it's channel id
        if method is 'user', then it's username
    """
    method, id = parse_channel_url(url)

    if method == 'channel':
        return id #id is already channel id
    elif method == "user":
        response = get_channel_details(youtube, forUsername=id) #make request to get channel id from user id
        items = response.get("items")
        if items:
            channel_id = items[0].get("id")
            return channel_id
        else:
            raise Exception(f"Cannot find channel ID corresponding to user ID: {id}")
    elif method == "c":
        #if id is a channel name, search for channel using channel name
        #not guaranteed to be correct
        response = search(youtube, q=id, maxResults=1)
        items = response.get("items")
        if items:
            channel_id = items[0]["snippet"]["channelId"]
            return channel_id
        else:
            raise Exception(f"Cannot find channel ID corresponding to channel name: {id}")
    raise Exception(f"Cannot find ID: {id} with {method} method")

def get_video_description(video_response):
    #returns video description lowercase with punctuation removed from video response 
    #this is gonna destroy links but whatever
    items = video_response.get("items")[0]
    snippet = items["snippet"]

    return snippet["description"].lower().strip("\n").strip(",")

def get_video_description_raw(video_response):
    return video_response.get("items")[0]["snippet"]["description"]

def parse_description_for_email(description):
    #takes in description string and returns email strings of the form name@domain.tld
    return re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', description)

def get_video_snippet(video_response):
    # gets stats from video response
    items = video_response.get("items")[0]
    return items["snippet"]

def get_video_statistics(video_response):
    # gets stats from video response
    items = video_response.get("items")[0]
    return items["statistics"]

def get_video_content_details(video_response):
    items = video_response.get("items")[0]
    return items["contentDetails"]

# test functions

def test_get_video_details(youtube):
    video_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw&ab_channel=jawed"
    # parse video ID from URL
    video_id = parse_video_url(video_url)
    # make API call to get video detail
    response = get_video_details(youtube, id=video_id)
    # print extracted video details
    print_video_details(response)

def test_search(youtube):
    # search for the q(uery) "sponsored" and retrieve 2 items only, ordered by view count
    response = search(youtube, q="sponsored", maxResults=2, order="viewCount", type="video")
    items = response.get("items")
    for item in items:
        video_id = item["id"]["videoId"] #get video ID
        video_response = get_video_details(youtube, id=video_id)
        print_video_details(video_response)
        print("="*50)

def test_get_channel_details(youtube):
    channel_url = "https://www.youtube.com/channel/UC8butISFwT-Wl7EV0hUK0BQ"
    # get the channel ID from the URL
    channel_id = get_channel_id_by_url(youtube, channel_url)
    # get the channel details
    response = get_channel_details(youtube, id=channel_id)
    # extract channel details
    snippet = response["items"][0]["snippet"]
    statistics = response["items"][0]["statistics"]

    channel_country = snippet["country"]
    channel_description = snippet["description"]
    channel_creation_date = snippet["publishedAt"]
    channel_title = snippet["title"]

    channel_subscriber_count = statistics["subscriberCount"]
    channel_video_count = statistics["videoCount"]
    channel_view_count  = statistics["viewCount"]

    print(f"""
    Title: {channel_title}
    Published At: {channel_creation_date}
    Description: {channel_description}
    Country: {channel_country}
    Number of videos: {channel_video_count}
    Number of subscribers: {channel_subscriber_count}
    Total views: {channel_view_count}
    """)

def test_get_channel_videos(youtube):
    channel_url = "https://www.youtube.com/channel/UC8butISFwT-Wl7EV0hUK0BQ"

    channel_id = get_channel_id_by_url(youtube, channel_url)

    n_pages = 2

    n_videos_count = 0
    next_page_token = None
    for i in range(n_pages):
        params = {
            'part': 'snippet',
            'q': '',
            'channelId': channel_id,
            'type': 'video',
        }

        if next_page_token:
            params['pageToken'] = next_page_token

        response = get_channel_videos(youtube, **params)
        channel_videos = response.get("items")

        for video in channel_videos:
            n_videos_count += 1
            video_id = video["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_response = get_video_details(youtube, id=video_id)
            print(f"================Video #{n_videos_count}================")
            # print the video details
            print_video_details(video_response)
            print(f"Video URL: {video_url}")
            print("="*40)
        print("*"*100)

        # if there is a next page add it to params to proceed to next page
        if "nextPageToken" in response:
            next_page_token = response["nextPageToken"]

def main():
    for credential in credentials:
        youtube = youtube_authenticate(credential)

        test_get_video_details(youtube)

    #test_search(youtube)
    
    #test_get_channel_details(youtube)

    #test_get_channel_videos(youtube)


if __name__ == "__main__":
    main()