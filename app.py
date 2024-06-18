from flask import Flask, render_template, request, redirect, flash
import secrets
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# Load the data
rvp = pd.read_csv('rvp_cleaned.csv')

# Define categories
categories = ['GEN', 'EWS', 'SC', 'ST', 'OBC-NCL']

# Create regressors for each category and PwD/non-PwD
regressors = {
    category: [
        create_regressor(rvp[rvp['CATEGORY'] == category]),
        create_regressor(rvp[rvp['CATEGORY'] == category + '-PwD'])
    ] for category in categories
}

def create_regressor(rvp_):
    X = rvp_['PERCENTILE'].values.reshape(-1, 1)
    y = rvp_['RANK'].values.reshape(-1, 1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)
    return regressor

def pvr(perc, pwd, category):
    x = pd.Series([perc])
    z = regressors[category][pwd == 'YES'].predict(x.values.reshape(-1, 1))
    k = float(np.round(z))
    if k <= 0:
        k = 15
    return k

# Import the finalList function from the algo module
from algo import finalList

@app.route("/", methods=["GET", "POST"])
def index():
    secret_key = secrets.token_hex(16)
    app.config["SECRET_KEY"] = secret_key

    if request.method == "POST":
        req = request.form

        percentile = req["percentile"]
        rank = req["rank"]
        state = req["state"]
        pwd = req["pwd"]
        gender = req["gender"]
        category = req["category"]
        sortby = str(req["sortby"])

        if percentile == "" and rank == "":
            flash("Please enter either your Rank or your Percentile", 'error')
            return redirect(request.url)

        if rank == "":
            ranks = pvr(float(percentile), pwd, category)
            ranks = int(ranks)

            if ranks <= 0:
                ranks = 2
            result = finalList(ranks, float(percentile), category, state, gender, pwd, sortby)

        if rank:
            result = finalList(int(rank), percentile, category, state, gender, pwd, sortby)
            ranks = rank

        return render_template("public/result.html", ranks=ranks, category=category, tables=[result.to_html(classes='data')], titles=result.columns.values)

    return render_template("public/index.html")

if __name__ == '__main__':
    app.run(debug=True)