"""nonempty"""
import requests
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

FORWARD_STEPS = 10

def get_data(address):
    """
    queries the data for the token

    address: address of the Uniswap contract
    """
    response = requests.get(f"https://api.covalenthq.com/v1/pricing/historical_by_addresses_v2/9001/USD/{address}/?from=2022-10-01&key=ckey_3c25e5ced5f74d099e39692d87a", timeout=5)
    data = response.json()
    date, price = [], []

    for x in range(len(data['data'][0]['prices'])):
        price.append(data['data'][0]['prices'][x]['price'])
        date.append(data['data'][0]['prices'][x]['date'])

    dataframe = pd.DataFrame({'date': date, 'price': price})
    dataframe = dataframe.sort_values(by='date').reset_index(drop=True)
    return dataframe

@app.route("/", methods=["GET","POST"])
def home():
    """prediction"""
    if request.args.get('a'):
        address = request.args.get('a')
    else:
        address = "0x3f75ceabCDfed1aCa03257Dc6Bdc0408E2b4b026"

    df_data = get_data(address)

    something = np.array(df_data.price[-5:])


    return jsonify({'data': something})
