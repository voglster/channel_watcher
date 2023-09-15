import os
from zoneinfo import ZoneInfo
import googleapiclient.discovery
import googleapiclient.errors
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import datetime
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve environment variables
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
CHANNEL_NAME = os.getenv("CHANNEL_NAME") or CHANNEL_ID
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3))  # Default to 3 hours
MAX_AGE = int(os.getenv("MAX_AGE", 7))  # Default to 3 hours
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

import googleapiclient.discovery
import googleapiclient.errors

def get_last_video_upload_time(api_key, channel_id):
    # Initialize the YouTube Data API client
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    try:
        # Get the channel's uploads playlist ID
        channel_response = youtube.channels().list(part="contentDetails", id=channel_id).execute()
        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Get the list of videos in the uploads playlist
        playlist_response = youtube.playlistItems().list(part="contentDetails", playlistId=uploads_playlist_id, maxResults=1).execute()

        if playlist_response.get("items"):
            # Get the ID of the last video in the playlist
            video_id = playlist_response["items"][0]["contentDetails"]["videoId"]

            # Get the video details including its snippet
            video_response = youtube.videos().list(part="snippet", id=video_id).execute()

            if video_response.get("items"):
                # Extract and return the publish date of the last video
                publish_time = video_response["items"][0]["snippet"]["publishedAt"]
                return publish_time
            else:
                return "No videos found in the channel."

        else:
            return "No videos found in the channel."

    except googleapiclient.errors.HttpError as e:
        return f"Error: {e}"


def get_time_difference(last_video_datetime, current_time):
    time_difference = current_time - last_video_datetime
    hours, remainder = divmod(time_difference.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(hours), int(minutes), int(seconds)

def check_last_video_time():
    current_time = datetime.datetime.now(ZoneInfo("UTC"))  # Ensure current_time is timezone-aware (in UTC)
    last_video_time = get_last_video_upload_time(API_KEY, CHANNEL_ID)

    if last_video_time:
        last_video_datetime = datetime.datetime.fromisoformat(last_video_time.replace("Z", "+00:00")).replace(tzinfo=ZoneInfo("UTC"))
        time_difference = current_time - last_video_datetime

        if time_difference.total_seconds() > MAX_AGE * 3600:  # 6 hours in seconds
            message = f"The last video is more than {MAX_AGE} hours old. Time since last video: {time_difference}"
            logger.error(message)
            post_to_slack(message)
        else:
            message = f"The last video was uploaded on: {last_video_datetime}. Time since last video: {time_difference}"
            logger.info(message)


def post_to_slack(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        logger.info("Message posted to Slack successfully.")
    else:
        logger.error(f"Failed to post message to Slack. Status code: {response.status_code}")

def main():
    logger.info("Starting the YouTube video checker...")
    check_last_video_time()
    scheduler = BlockingScheduler()

    # Schedule the check_last_video_time function to run every CHECK_INTERVAL hours
    scheduler.add_job(check_last_video_time, 'interval', hours=CHECK_INTERVAL)

    try:
        msg = f"Watching {CHANNEL_NAME}. Checking every {CHECK_INTERVAL} hours for last video over {MAX_AGE} hours ago."
        logger.info(msg)
        post_to_slack(msg)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
        post_to_slack("Scheduler stopped.")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        post_to_slack(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
