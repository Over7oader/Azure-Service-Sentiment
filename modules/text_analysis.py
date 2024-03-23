import re
from typing import List, Dict
from langdetect import detect
from azure.storage.blob import BlobServiceClient

CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=radiowezellogssapl;AccountKey=UZfIU2SsQh0e7seNeZAgB2Xkota6Atnfcn0OvmLu5jshiY7SxpSPWolD/QCwJXTzGtHquo/3Jpo7+AStLcQRjg==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "pythonfiles"
BLOB_NAME1 = "wulgaryzmy_pl.txt"
BLOB_NAME2 = "wulgaryzmy_en.txt"
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)
blob_client1 = container_client.get_blob_client(BLOB_NAME1)
blob_client2 = container_client.get_blob_client(BLOB_NAME2)

class TextAnalyzer:
    def __init__(self) -> None:
        pass

    def del_emoji(self, lyrics: str) -> str:
        pattern = re.compile("["
                             u"\U0001F600-\U0001F64F"
                             u"\U0001F300-\U0001F5FF"
                             u"\U0001F680-\U0001F6FF"
                             u"\U0001F1E0-\U0001F1FF"
                             u"\U00002500-\U00002BEF"
                             u"\U00002702-\U000027B0"
                             u"\U000024C2-\U0001F251"
                             u"\U0001f926-\U0001f937"
                             u"\U00010000-\U0010FFFF"
                             u"\u2640-\u2642"
                             u"\u2600-\u2B55"
                             u"\u200d"
                             u"\u23cf"
                             u"\u23e9"
                             u"\u231a"
                             u"\ufe0f"
                             u"\u3030"
                             "]+",
                             flags=re.UNICODE)
        return pattern.sub(r'', lyrics)

    def wulgaryzmy(self, text: str) -> str:
        profanity_pl_list = self._load_words(blob_client1)
        profanity_en_list = self._load_words(blob_client2)

        profanity_pl = self._count_occurrences(text, profanity_pl_list)
        profanity_en = self._count_occurrences(text, profanity_en_list)
        profanity_counter = sum(profanity_en.values())
        language = self._language_detection(text)
        combined_results = {**profanity_pl, **profanity_en}
        if combined_results and language in ['pl','en']:
            print('Swear words in text: ' + ', '.join(
                [f"{word} ({count})" for word, count in combined_results.items()]))
            language = self._language_detection(text)
            if language == 'pl':
                return "Too many swear words"  
            elif language == 'en' and profanity_counter <= 5:
                return '6 swear words or less'
            elif language == 'en' and profanity_counter > 5:
                return "Too many swear words"
        elif language not in ['pl','en']:
            return "Language not supported"
        else:
            return "Lyrics go to NLP model"
        
    def _count_occurrences(self,text: str, words: List[str]) -> Dict[str, int]:
        return {word: text.lower().count(word) for word in words if re.search(r'\b' + word + r'\b', text.lower())}

    def _load_words(self,filename: str) -> List[str]:
        with filename as blob:
            content = blob.download_blob()
            profanities = content.readall().decode('utf-8')
            profanities_list = profanities.splitlines()
            return profanities_list

    def _language_detection(self,text: str) -> str:
        jezyk = detect(text)
        return jezyk
        
