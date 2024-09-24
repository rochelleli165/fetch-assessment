from flask import Flask
from flask import request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route("/add", methods=["POST"])
def add():
    req = request.json
    payer = req['payer']
    points = req['points']
    timestamp = req['timestamp']

    if not payer or not points or not timestamp:
        return
    
    df = pd.read_csv('database.csv')

    new_rows = pd.DataFrame({'payer': [payer], 'points': [points], 'timestamp': [timestamp]})
    df = pd.concat([df, new_rows], ignore_index=True)

    df.to_csv('database.csv', index=False)
    return '', 200 

@app.route("/spend", methods=["POST"])
def spend():
    req = request.json
    points = req['points']

    if not points:
        return

    df = pd.read_csv('database.csv')
    df_sorted = df.sort_values(by='timestamp', ascending=True)
    df_sorted = df_sorted.reset_index()

    resp = {}
    tot = {}

    for index, row in df_sorted.iterrows():
        payer = row['payer']
        timestamp = row['timestamp']
        delta_points = row['points']
        if payer not in tot:
            tot[payer] = 0
            resp[payer] = 0
        
        tot[payer] += delta_points
        if points > 0:
            if points > delta_points:
                resp[payer] -= delta_points
                tot[payer] -= delta_points
                points -= delta_points
                df_sorted.loc[df_sorted['timestamp'] == timestamp, 'points'] = 0
            else:
                resp[payer] -= points
                tot[payer] -= points
                df_sorted.loc[df_sorted['timestamp'] == timestamp, 'points'] -= points
                points = 0

    if points > 0:
        return 'uh oh', 404
    for t in tot:
        if tot[t] < 0:
            return 'uh oh', 404
    
    df_sorted.to_csv('database.csv', index=False)
    return jsonify(resp)
    


@app.route("/balance", methods=['GET'])
def balance():
    df = pd.read_csv('database.csv')
    resp = {}
    for index, row in df.iterrows():
        payer = row['payer']
        if payer not in resp:
            resp[payer] = 0
        resp[payer] += row['points']
    return jsonify(resp)


if __name__ == '__main__':
    app.run(port=8000, debug=True)