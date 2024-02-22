from collections import namedtuple
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split

import json
import pandas as pd
import requests


url = 'http://eventregistry.org/api/v1/article/getArticles'

with open('newsapikey.txt') as keyfile:
    api_key = keyfile.read()

def get_data():
    with open('newsapikey.txt') as keyfile:
        api_key = keyfile.read()

    start_date = '2024-01-01'
    end_date = '2024-02-15'

    query_term = "wheat price"
    params = {
        "action": "getArticles",
        "keyword": query_term,
        "articlesPage": 1,
        "articlesCount": 100,
        "articlesSortBy": "rel",
        "articlesSortByAsc": True,
        "articlesArticleBodyLen": -1,
        "dateStart": start_date,
      #  "dateEnd": end_date,
        "isDuplicateFilter" : "skipDuplicates",
        "startSourceRankPercentile" : 20, 
        "lang": "eng",
       # "sourceLocationUri" : "https://en.wikipedia.org/wiki/United_States",
        "resultType": "articles",
        "dataType": [
            "news",
            "pr"
        ],
        "apiKey": api_key
    }
    print("Sent Request")
    response = requests.get(url = url, params = params)
    print(response)
    results = response.json()
    print(results['articles']['totalResults'])

    with open("articles.json", "w") as outfile:
        json.dump(results, outfile)

def build_model():
    with open('articles.json') as f:
        data = json.load(f)
    Article = namedtuple('article',['day','sentiment'])
    articles = tuple(Article(datetime.strptime(art['date'], '%Y-%m-%d'),art['sentiment']) for art in data['articles']['results'])

    sentiments = pd.DataFrame(data=articles).groupby('day').mean().reset_index()
    
    with open('data/HistoricalWheatPrices.csv') as csvfile:
        wp = pd.read_csv(csvfile)
        wp['Date'] = pd.to_datetime(wp['Date'])
       
    wp = wp[wp['Date'] >= sentiments['day'].min() - timedelta(days=7)]

    change = wp['Price'].pct_change()
    change.index -= 1
    wp.drop(wp.tail(1).index, inplace=True)

    wp['Change'] = change.iloc[1:]

    for x in range(1,8):
        nc = f'day_m{x}'
        wp[nc] = 0.0
        for ind in wp.index:
            # fwp[f'day_m{x}'][ind] = sentiments[sentiments['day'] == fwp['Date'][ind] - pd.Timedelta(days=x)]['sentiment']
            res = sentiments[sentiments['day'] == wp['Date'][ind] - pd.Timedelta(days=x)]
            if not res.empty:
                wp.loc[ind, nc] = res.iloc[0, res.columns.get_loc('sentiment')]
    return wp
                
def train_model(df):
    feature_cols = [f'day_m{x}' for x in range(1,8)]
    X = df[feature_cols]
    y = df.Change
        

train_model(build_model())