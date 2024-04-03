from flask import Flask, request
import pandas as pd

import os

USERS_PATH = os.path.join(os.getcwd(), "users.csv")
USER_DETAILS_PATH = os.path.join(os.getcwd(), "user_details.csv")


app = Flask(__name__)
users = pd.read_csv(USERS_PATH)
user_details = pd.read_csv(USER_DETAILS_PATH)


@app.route("/", methods=["GET"])
def home():
    return "Hi"

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        filter = users["name"].isin([name])

        if filter.sum() > 0:
            real_password = users[filter]["password"].values.tolist()[0]
            if password == real_password:
                return user_details[user_details["name"].isin([name])]["about"].values.tolist()[0]
            else:
                return "Incorrect password"
        else:
            return "Not an user"


if __name__ == "__main__":
    app.run(debug=True)
