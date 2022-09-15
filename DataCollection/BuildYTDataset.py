import logging
from datetime import datetime

import YoutubeAPI as yt

credentials = ["credentials.json", "credentials2.json", "credentials3.json"] #filenames of the OAuth credentials to bypass 10,000 point limit

video_keywords = ["college", "college admissions", "college life", "college vlog", "harvard life","harvard vlog", "ivy league", "ivy league move in", "dorm decor", "dorm organizing"]
description_keywords = ["sponsor", "use code", "sign up", "click the link", "use the link", "use my link", "click on the link", ]
false_keywords = ["not sponsor", "not a sponsor", "no sponsor", "isn't sponsored", "isnt sponsored"]
N_PAGES = 5 # number of pages of search results per keyword, n_pages * 50 will be the number of video results per term
MAX_RESULTS = 50 # number of results per search from 0-50

#I think using closely related search terms is probably pretty inefficient in terms of api points, its probably better to go deeper

video_keywords = ["turtleneck", "sweater", "dark academia fashion"] #testing smaller search term set

false_pos_count = 0 # number of descriptions with false keyword hits

cached_video_ids = [] # stores unique video ids searched
keyword_hits = {} # video_id: {vKey: search term used, dKey: keyword which first hit, ...}

run_stats = {
    'hits_per_keyword_per_search': {}, # 'search term': {'keyword': hits} 
}

#youtube = yt.youtube_authenticate() #youtube api key object

run_timestamp = datetime.now().strftime("%Y_%m_%d-%H:%M:%S_%p")

logging.basicConfig(filename=f"logs/yt_dataset_{run_timestamp}.log", filemode='w', format='%(levelname)s - %(message)s', level=logging.INFO)

logging.info(f"Starting run at {run_timestamp}")
logging.info(f"Using {len(video_keywords)} search terms")
logging.info(f"{MAX_RESULTS} results per page and {N_PAGES} pages per term")

logging.info(f"Approx {N_PAGES * len(video_keywords) * 100 * 2} API points will be used")

#THIS CODE NEEDS REFACTORING SOMETHING FIERCE

    # so right now its just gonna do the exact same search three times on different creds which isn't useful
    # either i need to build in exception handling and when the quota is met re authenticate with different credentials
    # or i need to track what i've searched through as to not repeat work across credentials
    # the search / get video details methods are what are gonna return the quota exceeded exception
    # dividing up the search terms and assigning a set few to each credential could work but breaks down as the number of keywords increases
    # I could also track the next page tokens and just have each set of credentials go through a set number of pages
    # exception handling is probably better tho sigh

    #okay new plan is to make a function which will do all the data collection for a specific keyword and page
    # i loop through the keywords and call findSponsors(youtube, keyword, page)
    # if a 403 quota exceeded error returns from the search, then the youtube object needs to change and the query rerun, but the current
    # keyword and page need to be maintained
    # maybe the error can be passed out of the search through the findSponsors function into the main controller

credential = 'credentials3.json'

with yt.youtube_authenticate(credential) as youtube:
    for vKey in video_keywords:

        # doing a lot of searches makes you reach the quota very fast
        # I doubt search results change all that fast so storing previous searches is probably a good idea

        next_page_token = None

        for i in range(N_PAGES):

            searchParams = {
                'q': vKey,
                'maxResults': MAX_RESULTS,
                'type': 'video', #i could make this a variable and collect channels and stuff too probably
            }

            if next_page_token is not None: # if a next page token comes in, use it
                searchParams['pageToken'] = next_page_token

            response = yt.search(youtube, **searchParams)
                
            if "nextPageToken" in response: # if there is a next page token, set it for next loop
                next_page_token = response["nextPageToken"]
            
            items = response.get("items")

            hit_count = 0

            # this loop handles what data are collected for each video
            for item in items:

                    video_id = item["id"]["videoId"] #get video ID

                    desc_snipped = item["snippet"]["description"]

                    if video_id not in cached_video_ids:
                        cached_video_ids.append(video_id)
                        logging.debug(f"New video ID: {video_id}, {len(cached_video_ids)} total")

                        vidTitle = item["snippet"]["title"]
                        channelTitle = item["snippet"]["channelTitle"]

                        video_response = yt.get_video_details(youtube, id=video_id)

                        statistics = yt.get_video_statistics(video_response)

                        video_details = yt.get_video_content_details(video_response)

                        desc = yt.get_video_description(video_response)

                        # # only need one hit
                        # if video_id not in keywordHits.keys():
                        #     if any(re.findall(''.join(descriptionKeywords), desc, re.IGNORECASE)):
                        #         #check for false positives
                        #         if not any(re.findall(''.join(falseKeywords), desc, re.IGNORECASE)):
                        #             # we lose specificty like this tho 
                        #             keywordHits[video_url] = {"vKey": vKey}
                        #             logging.info(f"Keyword found in description of video {video_id}")
                        
                        if video_id not in keyword_hits.keys():
                            false_pos = False #no false positive detected yet

                            for dKey in description_keywords:
                                if dKey in desc:
                                    # if hit, check for false positive
                                    for fKey in false_keywords:
                                        if fKey in desc:
                                            false_pos_count += 1 # am i interested in these false positive videos? probably eventually
                                            logging.warning(f"False key \"{fKey}\" found in description of video {video_id}")
                                            #no need to keep going after a false positive (?)
                                            false_pos = True
                                            break
                                    # if no false positive detected, log video
                                    if not false_pos:
                                        # this is where you set what you care about from the snippet
                                        emails = yt.parse_description_for_email(desc)
                                        keyword_hits[video_id] = {"vKey": vKey, "dKey": dKey, "desc": desc_snipped, "emails": emails,"title": vidTitle, "channelTitle": channelTitle}
                                        hit_count += 1
                                        logging.info(f"Keyword \"{dKey}\" found in description of video {video_id}")
                                        break
                                    else:
                                        # if false_pos, stop looking
                                        # if there is a double break idk about this wouldn't be necessary
                                        break
            
            logging.info(f"Found {hit_count} hits for search term \"{vKey}\" on page {i+1}")

            if false_pos_count > 0:
                logging.warning(f"Found {false_pos_count} false positives for search term \"{vKey}\"")
                false_pos_count = 0

logging.info(f"Found {len(keyword_hits)} total keyword hits out of {len(cached_video_ids)} videos")

with open(f'csv/sponsored_yt_vids_{run_timestamp}.csv', 'w') as csvfile:
    for key in keyword_hits.keys():
        csvfile.write(f"{key}, {keyword_hits[key]['vKey']}, {keyword_hits[key]['dKey']}, \"{keyword_hits[key]['desc']}\", {keyword_hits[key]['emails']}, {keyword_hits[key]['title']}, {keyword_hits[key]['channelTitle']}\n")
    