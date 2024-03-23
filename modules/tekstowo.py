import requests
import json
from bs4 import BeautifulSoup

class Tekstowo:
    def __init__(self) -> None:
        self.data = None
        self.song_info = None

    def get_data(self, url: str) -> None:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        self.data = soup
        
        script_tag = self.data.find('script', type = 'application/ld+json')
        script_content = script_tag.string
        self.song_info = json.loads(script_content)
    
    def get_author(self) -> str:
        author = self.song_info.get('byArtist', {}).get('name')
        return author

    def get_title(self) -> str:
        title = self.song_info.get('name')
        return title

    def get_lyrics(self) -> str:
        lyrics_div = self.data.find('div', class_ = 'inner-text')
        if lyrics_div:
            return "\n".join(line.strip() for line in lyrics_div.get_text().split("\n") if line.strip())
        else:
            return "Lyrics not found on the webpage"
