import csv
from flask import Flask, render_template, request
import pandas as pd
import os
import model
from model import get_review

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET','POST'])
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
