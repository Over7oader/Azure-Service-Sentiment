import torch
from transformers import pipeline, DistilBertTokenizer, DistilBertForSequenceClassification
from typing import Dict
from langdetect import detect

class SentimentAnalyzer:
    def __init__(self):
        self.tokenizer_en = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        self.model_en = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        self.nlp_pl = pipeline("sentiment-analysis", model="bardsai/twitter-sentiment-pl-base")

    def analyze(self, text: str) -> Dict:
        lang = detect(text)
        if lang == 'en':
            return self._analyze_en(text)
        elif lang == 'pl':
            return self._analyze_pl(text)
        else:
            raise ValueError("Unsupported language")

    def _analyze_en(self, text: str):
        fragments = self._split_text_into_fragments(text)
        scores = self._get_sentiment_scores(fragments, self.tokenizer_en, self.model_en)
        return self._aggregate_scores(scores)

    def _analyze_pl(self, text: str):
        fragments = self._split_text_into_fragments(text)
        scores = self._get_sentiment_scores_pl(fragments, self.nlp_pl)
        return self._aggregate_scores(scores)

    def _split_text_into_fragments(self, text: str):
        fragments = []
        current_fragment = ""
        fragment_length = 0

        for word in text.split(' '):
            if fragment_length + len(current_fragment) + len(word) > 256 or word.endswith('.'):
                fragments.append(current_fragment.strip())
                current_fragment = word
                fragment_length = len(word)
            else:
                current_fragment += ' ' + word
                fragment_length += len(word) + 1

        if current_fragment:
            fragments.append(current_fragment.strip())

        return fragments

    def _get_sentiment_scores(self, fragments, tokenizer, model):
        scores = []
        for fragment in fragments:
            inputs = tokenizer(fragment, return_tensors="pt")
            with torch.no_grad():
                logits = model(**inputs).logits

            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            positive_score = probabilities[0][model.config.label2id['POSITIVE']].item()
            negative_score = probabilities[0][model.config.label2id['NEGATIVE']].item()

            label = 'POSITIVE' if positive_score > negative_score else 'NEGATIVE'
            score = max(positive_score, negative_score)

            scores.append({'label': label, 'score': score})

        return scores

    def _get_sentiment_scores_pl(self, fragments, nlp):
        scores = []
        for fragment in fragments:
            sentyment = nlp(fragment)
            scores.append({'label': sentyment[0]['label'], 'score': sentyment[0]['score']})
        return scores

    def _aggregate_scores(self, scores):
        overall_result = {'label': 'neutral', 'score': 0}
        labels_count = {'positive': 0, 'negative': 0, 'neutral': 0}  

        for score in scores:
            label = score['label'].lower()  
            overall_result['score'] += score['score']
            labels_count[label] += 1

        dominant_label = max(labels_count, key=labels_count.get)
        if labels_count[dominant_label] / len(scores) < 0.5: 
            overall_result['label'] = 'negative'
        else:
            overall_result['label'] = dominant_label.upper() 
        overall_result['score'] /= len(scores)

        return overall_result
