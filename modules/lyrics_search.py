import re
import requests
import urllib
from bs4 import BeautifulSoup
from typing import Optional

from .tekstowo import Tekstowo
from .genius import Genius

class GetLyricsOutsideYT:
    def __init__(self) -> None:
        pass

    def search_lyrics_yahoo(self,title: str) -> Optional[str]:
        url = f"https://search.yahoo.com/search?q={title} lyrics tekstowo genius".replace(" ", "%20")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            link_d = link.get('href')
            fields = link_d.split('/')
            for part in fields:
                try:
                    if part.startswith('RU='):
                        url = urllib.parse.unquote(str(part).split('=')[1])
                        if "https://genius.com/" in url and "-lyrics" in url:
                            genius = Genius()
                            data = genius.get_data(url)  
                            author = genius.get_author()
                            title = genius.get_title()
                            lyrics = genius.get_lyrics()
                            return lyrics

                        elif "https://www.tekstowo.pl/piosenka," in url:
                            tekstowo = Tekstowo()
                            data = tekstowo.get_data(url)
                            author = tekstowo.get_author()
                            title = tekstowo.get_title()
                            lyrics = tekstowo.get_lyrics()
                            return lyrics
                except Exception as e:
                    return None
            
        return None
