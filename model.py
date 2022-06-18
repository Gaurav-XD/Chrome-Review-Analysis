import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def get_review(dataframe):
    lemmatizer = WordNetLemmatizer()
    all_reviews = dataframe
    print(all_reviews.head())

    sw_clean = set(stopwords.words('english'))
    sw_clean.remove('not')
    sw_clean.remove('no')
    new_review = []
    for review in all_reviews['Text']:
        review = re.sub(r'[^\w\s]', '', str(review))
        review = re.sub(r'\d','',review)
        review_token = word_tokenize(review.lower().strip())
        r_without_stop = []
        for word in review_token:
            if word not in sw_clean:
                word = lemmatizer.lemmatize(word)
                r_without_stop.append(word)
        clean_review = " ".join(r_without_stop)
        new_review.append(clean_review)
    all_reviews['New_Text'] = new_review
    req_review = all_reviews[all_reviews.Star <= 3]
    sentiment_model = SentimentIntensityAnalyzer()
    senti_list = []
    for review in req_review['New_Text']:
        score = sentiment_model.polarity_scores(review)
        if score['pos'] >= 0.7:
            senti_list.append('+')
        else:
            senti_list.append('-')
    req_review["sentiment"] = senti_list
    final_review = req_review[req_review.sentiment == '+']
    final_review.drop('New_Text', axis = 1,inplace=True)
    return final_review
