import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.blocking import BlockingScheduler

# YouTube API setup
api_key = os.environ['YOUTUBE_API_KEY']  # Use environment variables for sensitive data
youtube = build('youtube', 'v3', developerKey=api_key)

# Updated list of channels to monitor
channel_ids = {
    "Dylan_Anderson": "UCpuT8AlP9P9EgW_pZ0_xInQ", 
    "gritness": "UCYUmpFvruZi95kePOV7r6jw", 
    "Wholesomeanimalss": "UCmX7Iw8rYnSEB3Q-vk3dKjQ", 
    "Newsnercom": "UCYCxYp7o8PZuer5vTGzuEUg", 
    "DailyDoseOfMasculinity": "UCgGMOPxZ38TozReX2o75A9w", 
    "NoxJackson": "UCiMg6RqrpxydecVeQNHihxg", 
    "FitFixx": "UC3NJVkGUkPwvWwWpQG-67Ag", 
    "CopHumor": "UCW2R_zesOCCKqkNj4lJZ77A", 
    "StoriesWithGui": "UCEr1YRAxCj82jSbSlGd0T4Q", 
    "Mr.Fascinavo": "UCC4fPQV_YEZfH7VLvWkhHSw", 
    "Satoshi.Stories": "UC-Ya-c4FvAHnf2-NgzYPZUw",
    "VidXiv": "UCPzXfSbhQ3xn2Y7JJ2-7lZw",
    "SideVid": "UCyWd5KH5oEwL01mMO2yiIdw",
    "DavidWilsonStories": "UCJcDnxsGrWHEOzSnIn7uqlA",
    "Jasper_Storm": "UCrFxNu9_6AX3yks5yXWlceQ", 
    "Captain_Nox": "UC3E1K1ZSOMqAWTOZpgMS1cw", 
    "MediaConquer": "UCDc1UerYL73gScmcQrnpv6w", 
    "FactasticFeed": "UCoGcvX8WSTOpK52Y81OfVFg", 
    "MerriMash": "UCIWdsXpjhkS9jjuwSJvXcTg"
}

def get_recent_shorts(channel_id):
    # Get channel's uploads playlist
    response = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get videos uploaded in last 24 hours
    one_day_ago = (datetime.utcnow() - timedelta(days=1)).isoformat("T") + "Z"
    videos = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=50
    ).execute()

    # Filter for Shorts (videos < 60 seconds)
    shorts = []
    for video in videos['items']:
        video_id = video['snippet']['resourceId']['videoId']
        video_details = youtube.videos().list(
            part='contentDetails',
            id=video_id
        ).execute()
        duration = video_details['items'][0]['contentDetails']['duration']
        if "PT" in duration and "M" not in duration:  # It's less than 60 seconds
            shorts.append(f"https://youtube.com/shorts/{video_id}")
    return shorts

def send_email(links):
    # Send email notification
    sender_email = os.environ['SENDER_EMAIL']
    receiver_email = os.environ['RECEIVER_EMAIL']
    sender_password = os.environ['SENDER_PASSWORD']

    msg = MIMEText('\n'.join(links))
    msg['Subject'] = 'Daily YouTube Shorts'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()

def check_for_new_shorts():
    all_shorts = []
    for channel_name, channel_id in channel_ids.items():
        shorts = get_recent_shorts(channel_id)
        if shorts:
            all_shorts.append(f"Channel: {channel_name}")
            all_shorts.extend(shorts)
            all_shorts.append("")  # Add empty line between different channels

    if all_shorts:
        send_email(all_shorts)
    else:
        print("No new shorts uploaded today.")

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(check_for_new_shorts, 'interval', hours=24)  # Check daily
    scheduler.start()
