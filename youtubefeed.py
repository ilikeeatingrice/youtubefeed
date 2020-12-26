import os

import googleapiclient.discovery
import googleapiclient.errors
from datetime import datetime, timedelta
import smtplib 

scopes = []
channelIds = []
fresh = datetime.now() - timedelta(hours=24)

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey="key")

    playlistIds = getChannels(channelIds, youtube)
    videos = getNewVideoIdsFromList(playlistIds, youtube, fresh)
    message = '\n'.join(videos)
    message = "NEW VIDEOS\n\n"+message
    print(message)
    email(message)

def getChannels(channelIds, youtubeClient):
    playlistIds = []
    for chid in channelIds:
        request = youtubeClient.channels().list(
            part="snippet,contentDetails,statistics",
            id=chid
        )
        response = request.execute()
        for item in response["items"]:
            playlistIds.append(item["contentDetails"]["relatedPlaylists"]["uploads"])
    return playlistIds

def getNewVideoIdsFromList(playlistIds, youtubeClient, fresh):
    videos = []
    for playlistId in playlistIds:
        request = youtubeClient.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlistId
        )
        response = request.execute()
        latestVideo = response["items"][0]
        videotime = datetime.strptime(latestVideo["contentDetails"]["videoPublishedAt"], "%Y-%m-%dT%H:%M:%SZ") #"2020-12-25T09:12:56Z"
        if videotime < fresh:
            continue
        videos.append(extractVideoInfo(latestVideo))
    return videos

def extractVideoInfo(video):
    result = ''
    result+= ('title:' + video["snippet"]["title"]+"\n")
    result+= ('description:' + video["snippet"]["description"]+"\n")
    result+= ('url:' + "https://www.youtube.com/watch?v="+video["contentDetails"]["videoId"]+"\n")
    return result

def email(str):
        # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    # start TLS for security 
    s.starttls() 
    # Authentication 
    s.login("emailaddress", "password") 
    # message to be sent 
    message = str.encode('utf8')
    # sending the mail 
    s.sendmail("emailaddress", "emailaddress", message) 
    # terminating the session 
    s.quit() 
        
if __name__ == "__main__":
    main()