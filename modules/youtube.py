import re
import requests
from bs4 import BeautifulSoup
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from azure.storage.blob import BlobServiceClient

CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=radiowezellogssapl;AccountKey=UZfIU2SsQh0e7seNeZAgB2Xkota6Atnfcn0OvmLu5jshiY7SxpSPWolD/QCwJXTzGtHquo/3Jpo7+AStLcQRjg==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "pythonfiles"
BLOB_NAME1 = "wulgaryzmy_pl.txt"
BLOB_NAME2 = "wulgaryzmy_en.txt"
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)
blob_client1 = container_client.get_blob_client(BLOB_NAME1)
blob_client2 = container_client.get_blob_client(BLOB_NAME2)
class Youtube:
    def __init__(self) -> None:
        self.data = None

    def get_data(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            self.data = soup
            return soup
        except Exception as e:
            return None

    def get_title(self) -> Optional[str]:
        try:
            title = self.data.title.string
            modified_title = re.sub(r"\[.*?\]|\(.*?\)| - YouTube|&amp;", "", title.split('|')[0])
            with blob_client1 as blob:
                content = blob.download_blob()
                profanities = content.readall().decode('utf-8')
                polish_blacklist = profanities.splitlines()
            with blob_client2 as blob:
                content = blob.download_blob()
                profanities = content.readall().decode('utf-8')
                english_blacklist = profanities.splitlines()

            combined_blacklist = polish_blacklist + english_blacklist
            for word in combined_blacklist:
                if re.search(rf'\b{re.escape(word)}\b', title, re.IGNORECASE):
                    return None

            return modified_title
        except Exception as e:
            return None
            
    def get_video_id(self, link: str) -> Optional[str]:
        try:
            video_id = re.search(r"v=([a-zA-Z0-9_-]{11})", link)
            return video_id.group(1) if video_id else None
        except Exception as e:
            return None

    def get_lyrics(self, video_id: str) -> Optional[str]:
        try:
            if video_id:
                transcript_pl = YouTubeTranscriptApi.get_transcript(video_id, languages=['pl'])
                if transcript_pl:
                    text_pl = ' '.join([fragment['text'] for fragment in transcript_pl])
                    return text_pl

                transcript_en = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                if transcript_en:
                    text_en = ' '.join([fragment['text'] for fragment in transcript_en])
                    return text_en

            return None
        except Exception as e:
            return None
