from .youtube import Youtube
from .lyrics_search import GetLyricsOutsideYT

def process_song(link: str) -> str:
    try:
        yt = Youtube()
        yt_html = yt.get_data(link)
        if not yt_html:
            return "Failed to fetch YouTube data"

        title = yt.get_title()
        if not title:
            return "Failed to fetch title from YouTube"

        video_id = yt.get_video_id(link)
        if not video_id:
            return "Failed to extract video ID from YouTube link"

        print("Processing YouTube transcript...")
        youtube_transcript = yt.get_lyrics(video_id)
        if youtube_transcript:
            return youtube_transcript.lower()

        print("Trying external sources for lyrics...")
        external_lyrics = GetLyricsOutsideYT()
        lyrics = external_lyrics.search_lyrics_yahoo(title)
        if lyrics:
            print("Lyrics retrieved from external source")
            return lyrics.lower()

        return "Lyrics not found"
    except Exception as e:
        return "An error occurred while processing the song"

if __name__ == "__main__":
    link = input("Enter YouTube link: ")
    print(process_song(link))
