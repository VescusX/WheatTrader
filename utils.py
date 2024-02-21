from datetime import datetime

import json
import pandas as pd
import requests

url = 'http://eventregistry.org/api/v1/article/getArticles'

with open('newsapikey.txt') as keyfile:
    api_key = keyfile.read()

def get_data():
    with open('data/HistoricalWheatPrices.csv') as csvfile:
        wp = pd.read_csv(csvfile)
        #wp.index = pd.to_datetime(wp['Date'])
       
    fwp = wp[pd.to_datetime(wp['Date']) >= datetime(2023,8,1)]

    start_date = '2023-09-01'
    end_date = '2023-09-04'

    query_term = "price wheat"
    params = {
        "action": "getArticles",
        "keyword": query_term,
        "articlesPage": 1,
        "articlesCount": 10,
        "articlesSortBy": "rel",
        "articlesSortByAsc": False,
        "articlesArticleBodyLen": -1,
        "dateStart": start_date,
        "dateEnd": end_date,
        "isDuplicateFilter" : "skipDuplicates",
        "startSourceRankPercentile" : 30, 
        "lang": "eng",
        "sourceLocationUri" : "https://en.wikipedia.org/wiki/United_States",
        "resultType": "articles",
        "dataType": [
            "news",
            "pr"
        ],
        "apiKey": api_key
        #"forceMaxDataTimeWindow": 31 # parameter is overwritten by dateStart
    }
    print("Sent Request")
    response = requests.get(url = url, params = params)
    print(response)
    print(response.json())

    with open("articles.json", "w") as outfile:
        json.dump(response.json(), outfile)

       
       
        

get_data()