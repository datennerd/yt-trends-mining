"""Collecting regional YouTube trends with the YouTube Data API."""

import os
import time
from datetime import datetime

from apiclient.discovery import build
from pandas import DataFrame


def get_i18nRegions():
    """Get region codes

    ISO 3166-1 alpha-2 codes:
      https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

    Returns:
      pandas.core.frame.DataFrame
    """
    req = youtube.i18nRegions().list(part="snippet").execute()["items"]

    gl = [i["snippet"]["gl"] for i in req]
    name = [i["snippet"]["name"] for i in req]

    return DataFrame({"gl": gl, "name": name})


def get_video_categories(region_code):
    """Get video category ids and titles of a certain country.

    Args:
      region_code: string
        ISO 3166-1 alpha-2 codes of an country, i.e. "DE", "US"

    Returns:
      pandas.core.frame.DataFrame
    """
    req = (
        youtube.videoCategories()
        .list(part="snippet", regionCode=region_code)
        .execute()["items"]
    )

    video_categoy_ids = [i["id"] for i in req]
    video_categoy_title = [i["snippet"]["title"] for i in req]
    video_categoy_assignable = [i["snippet"]["assignable"] for i in req]

    return DataFrame(
        {
            "videoCategoyIds": video_categoy_ids,
            "videoCategoyTitle": video_categoy_title,
            "videoCategoyAssignable": video_categoy_assignable,
        }
    )


def get_trending_videos(region_code, max_results=250):
    """Collecting trend page video information of a certain country.

    Args:
      region_codes: string
        ISO 3166-1 alpha-2 codes of an country, i.e. "DE", "US"
      max_results: integer
        Number of results

    Returns:
      pandas.core.frame.DataFrame
    """
    req = (
        youtube.videos()
        .list(
            part="snippet, statistics, contentDetails, topicDetails",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=max_results,
        )
        .execute()["items"]
    )

    # Snippet
    sequence = list(range(1, len(req) + 1))
    today = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    video_ids = [i["id"] for i in req]
    published_at = [i["snippet"]["publishedAt"] for i in req]
    titles = [i["snippet"]["title"] for i in req]
    channel_ids = [i["snippet"]["channelId"] for i in req]
    channel_titles = [i["snippet"]["channelTitle"] for i in req]
    thumbnails = [i["snippet"]["thumbnails"]["default"]["url"] for i in req]
    category_ids = [i["snippet"]["categoryId"] for i in req]
    descriptions = [i["snippet"]["description"] for i in req]
    tags = [i["snippet"].get("tags", None) for i in req]

    # Statistics
    views = [i["statistics"].get("viewCount", None) for i in req]
    likes = [i["statistics"].get("likeCount", None) for i in req]
    dislikes = [i["statistics"].get("dislikeCount", None) for i in req]
    comments = [i["statistics"].get("commentCount", None) for i in req]

    # ContentDetails
    durations = [i["contentDetails"]["duration"] for i in req]
    region_restrictions = [
        i["contentDetails"].get("regionRestriction", None) for i in req
    ]

    # TopicDetails
    topic_details = [i.get("topicDetails", {}) for i in req]
    relevant_topic_ids = [i.get("relevantTopicIds", None) for i in topic_details]

    return DataFrame(
        {
            "sequence": sequence,
            "today": today,
            "videoIds": video_ids,
            "publishedAt": published_at,
            "titles": titles,
            "channelIds": channel_ids,
            "channelTitles": channel_titles,
            "thumbnails": thumbnails,
            "categoryIds": category_ids,
            "descriptions": descriptions,
            "tags": tags,
            "views": views,
            "likes": likes,
            "dislikes": dislikes,
            "comments": comments,
            "durations": durations,
            "regionRestrictions": region_restrictions,
            "relevantTopicIds": relevant_topic_ids,
        }
    )


def get_channel_features(channel_ids, max_results=250):
    """Get channel features.

    Args:
      channel_ids: list
        Expects a list of channel Ids
      max_results: integer
        Number of results

    Returns:
      pandas.core.frame.DataFrame
    """
    req = (
        youtube.channels()
        .list(
            id=",".join(channel_ids),
            part="snippet, statistics, topicDetails",
            maxResults=max_results,
        )
        .execute()["items"]
    )

    # Snippet
    channel_join_ids = [i["id"] for i in req]
    channel_published_at = [i["snippet"]["publishedAt"] for i in req]
    channel_country = [i["snippet"].get("country", None) for i in req]

    # Statistics
    channel_view_count = [i["statistics"]["viewCount"] for i in req]
    channel_subscriber_count = [
        i["statistics"].get("subscriberCount", None) for i in req
    ]
    channel_video_count = [i["statistics"]["videoCount"] for i in req]

    # TopicDetails
    topic_details = [i.get("topicDetails", {}) for i in req]
    channel_topic_ids = [i.get("topicIds", None) for i in topic_details]

    return DataFrame(
        {
            "channelJoinIds": channel_join_ids,
            "channelPublishedAt": channel_published_at,
            "channelCountry": channel_country,
            "channelViewCount": channel_view_count,
            "channelSubscriberCount": channel_subscriber_count,
            "channelVideoCount": channel_video_count,
            "channelTopicIds": channel_topic_ids,
        }
    )


if __name__ == "__main__":

    # Ressource object to interact with any Google API
    youtube = build("youtube", "v3", developerKey=os.environ["API_KEY"])

    # Top 10 leading countries based on YouTube users
    regionCodes = ["US", "BR", "RU", "JP", "IN", "GB", "DE", "FR", "CA", "AU"]

    for regionCode in regionCodes:

        # Collect video and channel informations
        time.sleep(3)
        df_trends = get_trending_videos(regionCode)
        time.sleep(3)
        df_channels = get_channel_features(df_trends["channelIds"])
        df = df_trends.join(df_channels.set_index("channelJoinIds"), on="channelIds")

        # Save DataFrame as CSV
        filename = f"{datetime.today().strftime('%Y%m%d')}_{regionCode}.csv"
        df.to_csv(f"data/{filename}")
