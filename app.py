from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Union
from azure.storage.blob import BlobServiceClient
from datetime import datetime

from modules.youtube import Youtube
from modules.text_analysis import TextAnalyzer
from modules.sentiment_analysis import SentimentAnalyzer
from modules.main import process_song

app = Flask(__name__)
CORS(app)

CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=radiowezellogssapl;AccountKey=UZfIU2SsQh0e7seNeZAgB2Xkota6Atnfcn0OvmLu5jshiY7SxpSPWolD/QCwJXTzGtHquo/3Jpo7+AStLcQRjg==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "pythonlogs"
BLOB_NAME = "pythonlog.txt"
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)
blob_client = container_client.get_blob_client(BLOB_NAME)
def Blob(message,status):
    c = datetime.now()
    current_day = c.strftime('%Y-%m-%d')
    current_time = c.strftime('%H:%M:%S')
    blob_client.append_block(f"[{current_day} {current_time} {status}] {message}\n")
@app.route("/sentiment", methods=["POST"])
def analyze_sentiment() -> Dict[str, Union[float, str]]:
    try:
        data = request.json
        link = data.get("URL")
        Blob(f"Received URL: {link}", "INFO")

        youtube = Youtube()
        youtube.get_data(link)
        title = youtube.get_title()
        if not title:
            Blob(f"Title include banned words", "INFO")
            return jsonify({"sentiment": 2}), 200
        Blob(f"Title extracted from YouTube: {title}", "INFO")

        lyrics = process_song(link)
        if lyrics:
            Blob("Lyrics extracted successfully", "INFO")

            cleaned_lyrics = TextAnalyzer().del_emoji(lyrics)
            Blob("Lyrics cleaned from emojis", "INFO")

            vulgarity_check = TextAnalyzer().wulgaryzmy(cleaned_lyrics)
            Blob(f"Vulgarity check result: {vulgarity_check}", "INFO")

            if '6 swear words or less' in vulgarity_check or "Lyrics go to NLP model" in vulgarity_check:
                Blob("Sentiment analysis initiated", "INFO")
                sentiment_result = SentimentAnalyzer().analyze(cleaned_lyrics)
                Blob(f"Sentiment result: {sentiment_result}", "INFO")

                sentiment_score = None
                if sentiment_result["label"] == "POSITIVE":
                    sentiment_score = 0
                elif sentiment_result["label"] == "NEUTRAL":
                    sentiment_score = 1
                else:
                    sentiment_score = 2

                Blob(f"Final sentiment score: {sentiment_score}", "INFO")
                return jsonify({"sentiment": sentiment_score}), 200
            else:
                Blob("Too many swear words detected, unable to analyze sentiment", "WARNING")
                return jsonify({"sentiment": 2}), 200
    except Exception as e:
        Blob(f"Error occurred: {str(e)}", "ERROR")
        return jsonify({"Error": str(e)}), 400

 
if __name__ == '__main__':
    #logging.getLogger().addHandler(Blob)
    app.run(debug=True, port=5000, threaded=True)