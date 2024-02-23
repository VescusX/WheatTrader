from flask import Flask
from flask_cors import CORS

from utils import make_prediction

import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/daily_prediction')
def submit_text():
    day = pd.to_datetime('today').normalize()
    return {'prediction': make_prediction(day), 'day': day.strftime('%Y-%m-%d')}