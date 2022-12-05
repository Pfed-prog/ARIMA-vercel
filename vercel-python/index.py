"""nonempty"""
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)


FORWARD_STEPS = 10


def lin_regr_func(x, y):
    """
    linear regression
    """
    n = len(x)
    # denominator
    d = (n*(x**2).sum()-x.sum()**2)
    # intercept
    a = (y.sum()*(x**2).sum()-x.sum()*(x*y).sum()) / d
    # slope
    b = (n*(x*y).sum()-x.sum()*y.sum())/d
    return a, b

def get_data(address):
    """
    queries the data for the token

    address: address of the Uniswap contract
    """
    response = requests.get(f"https://api.covalenthq.com/v1/pricing/historical_by_addresses_v2/9001/USD/{address}/?from=2022-10-01&key=ckey_3c25e5ced5f74d099e39692d87a", timeout=5)
    data = response.json()
    date, price = [], []

    for day in range(len(data['data'][0]['prices'])):
        price.append(data['data'][0]['prices'][day]['price'])
        date.append(data['data'][0]['prices'][day]['date'])

    dataframe = pd.DataFrame({'date': date, 'price': price})
    dataframe = dataframe.sort_values(by='date').reset_index(drop=True)
    dataframe['price_1'] = dataframe.price.shift(1)
    return dataframe

@app.route("/", methods=["GET","POST"])
def home():
    """prediction"""
    if request.args.get('a'):
        address = request.args.get('a')
    else:
        address = "0x3f75ceabCDfed1aCa03257Dc6Bdc0408E2b4b026"

    df_data = get_data(address)

    intercept, coef = lin_regr_func(df_data.price_1, df_data.price)
    predictions = []
    last_value = df_data.price.iloc[-1]
    for _ in range(FORWARD_STEPS):
        predictions.append(intercept + coef*last_value)
        last_value = intercept + coef*last_value

    return jsonify({'prediction': predictions, 'last_date': str(df_data.date.iloc[-1])})
