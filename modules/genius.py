import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Optional

class Genius:
    def __init__(self) -> None:
        self.data = None
        self.song_info = None
    
    def get_data(self, url: str) -> None:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        self.data = soup

        script_tags = self.data.find_all('script')
        target_script = None

        for script in script_tags:
            if 'var targeting_list =' in script.text:
                target_script = script.text
                break

        if target_script:
            match = re.search(r'var targeting_list = (\[.*?\]);', target_script)
            if match:
                js_fragment = match.group(1)
                self.song_info = json.loads(js_fragment)

    def get_author(self) -> List[str]:
        author = None
        for item in self.song_info:
            if item['name'] == 'artist_name':
                author = item['values']
        return author

    def get_title(self) -> Optional[str]:
        title = None
        for item in self.song_info:
            if item['name'] == 'song_title':
                title = item['values'][0]
        return title

    def get_lyrics(self) -> Optional[str]:
        lyrics_containers = self.data.find_all('div', {'class': 'Lyrics__Container-sc-1ynbvzw-1 kUgSbL'})
        lyrics_text = ''

        for container in lyrics_containers:
            lyrics_text += container.get_text(separator='\n') + '\n\n'

        lyrics_text = re.sub(r"\[.*?\]", "", lyrics_text)

        return lyrics_text
