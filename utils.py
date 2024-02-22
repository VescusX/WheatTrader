from collections import namedtuple
from datetime import datetime
from sklearn.linear_model import LinearRegression, LogisticRegression

import json
import pandas as pd
import requests


url = 'http://eventregistry.org/api/v1/article/getArticles'

with open('newsapikey.txt') as keyfile:
    api_key = keyfile.read()

def retrieve_data():
    with open('newsapikey.txt') as keyfile:
        api_key = keyfile.read()

    start_date = '2024-01-01'
    end_date = '2024-02-15'

    #Parameters for API key
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
    print("Retrieved ", results['articles']['totalResults'], " results")


    with open("sentiments_articles.pkl", "wb") as outfile:
        articles = pd.DataFrame({ 'day': datetime.strptime(art['date'], '%Y-%m-%d'), 
                                 'sentiment': art['sentiment'],
                                 'link' : art['url']}
                                 for art in results['articles']['results'])
        articles.to_pickle("sentiments_articles.pkl")

def prepare_data():
    #Get the sentiment of the articles
    articles = pd.read_pickle("sentiments_articles.pkl").drop(['link'],axis=1)

    #Find the average sentiment per day
    sentiments = articles.groupby('day').mean().reset_index()
    
    #Get Wheat Prices
    with open('data/HistoricalWheatPrices.csv') as csvfile:
        wp = pd.read_csv(csvfile)
        wp['Date'] = pd.to_datetime(wp['Date'])
       

    #Filter out days with no sentiments
    wp = wp[wp['Date'] >= sentiments['day'].min()]
   
    #Add the percentage change to the next day
    change = wp['Price'].pct_change()
    change.index -= 1
    wp.drop(wp.tail(1).index, inplace=True)
    wp['Change'] = change.iloc[1:]
    wp['Direction'] = wp.apply(lambda r : 'rise' if r.Change >= 0 else 'fall', axis = 1)

    #Add sentiments for the previous 7 days
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
    #Train model
    feature_cols = [f'day_m{x}' for x in range(1,8)]
    X = df[feature_cols]
    yi = df.Change
    yo = df.Direction

    linreg = LinearRegression()
    linreg.fit(X, yi)
    logreg = LogisticRegression(random_state=29) # Set random_state for reproducibility
    logreg.fit(X, yo)

    sd = (0,0,.074510,0,0,-0.388235,-0.100654)

    tyer = pd.DataFrame(data = {f'day_m{i+1}': [s] for i, s in enumerate(sd) })
    # print(tyer)
    for n in range(X.shape[0]):
        m = X.iloc[n:n+1]
        # print(m)
        # print(yi.iloc[n])
        # print('\t',linreg.predict(m))
        # print('\t',logreg.predict(m))

    #print(linreg.print)
        
# retrieve_data()
train_model(prepare_data())