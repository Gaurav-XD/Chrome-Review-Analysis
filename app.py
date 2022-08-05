import csv
from flask import Flask, render_template, request, make_response
from functools import wraps
import pandas as pd
import os
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

app = Flask(__name__)

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == "nextlab" and auth.password == "nextlab123":
            return f(*args, **kwargs)
        return make_response('Could not verify your login!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    return decorated        

@app.route('/', methods=['GET','POST'])
def index():
    if request.authorization and request.authorization.username == "nextlab" and request.authorization.password == "nextlab123":
        return render_template('index.html')
    return make_response('Could not verify your login!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

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

@app.route('/data', methods=['GET','POST'])
@auth_required
def csv_to_df():
    if request.method == 'POST':
        inputcsv = request.files['csvfile']
        if not os.path.isdir('static'):
            os.mkdir('static')
        filepath = os.path.join('static',inputcsv.filename)
        inputcsv.save(filepath)
        

        data=[]
        with open(filepath, encoding = 'utf8') as file:
            csvfile = csv.reader(file)
            for row in csvfile:
                data.append(row)
        print(type(data))
        dataframe = pd.DataFrame(data)
        dataframe.to_csv('sample.csv',header=False, index = False)
        dataframe = pd.read_csv('sample.csv')
        review = get_review(dataframe)
        return render_template('data.html', data=review.to_html(header=True,index=False))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
