# Can be found on dockerhub
`docker pull voglster/channel_watcher`

# YouTube Video Checker with Slack Notifications

This Python script checks the upload time of the latest video on a specified YouTube channel and sends a notification to a Slack channel if the last video was uploaded more than 6 hours ago.

## Prerequisites

Before running this script, you need to set up the following:

1. **YouTube Data API Key:** You will need a YouTube Data API Key to access YouTube channel data. You can obtain one by following the instructions [here](https://developers.google.com/youtube/registering_an_application).

2. **YouTube Channel ID:** You must specify the YouTube channel ID of the channel you want to monitor. You can find the channel ID in the URL of the channel's page.

3. **Slack Webhook URL (Optional):** If you want to receive Slack notifications, you'll need a Slack webhook URL. You can create one by following the instructions [here](https://api.slack.com/messaging/webhooks).

## Installation

1. Clone this repository to your local machine.

2. Create a `.env` file in the project directory with the following content:

YOUTUBE_API_KEY=<Your YouTube API Key>
YOUTUBE_CHANNEL_ID=<Your YouTube Channel ID>
SLACK_WEBHOOK_URL=<Your Slack Webhook URL>

Replace the placeholders with your actual API key, channel ID, and Slack webhook URL.

3. Build the Docker image:

`docker build -t youtube-video-checker .`

## Usage

To run the script and schedule periodic checks, execute the following Docker command:

`docker run --rm --env-file .env youtube-video-checker`

optionally throw in a -d to daemonize it

The script will check the last video upload time every 3 hours by default. If the last video was uploaded more than 6 hours ago, it will send a notification to the specified Slack channel (if a webhook URL is provided).

