from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import pandas as pd
import os

USERS_PATH = os.path.join(os.getcwd(), "users.csv")
USER_DETAILS_PATH = os.path.join(os.getcwd(), "user_details.csv")
users = pd.read_csv(USERS_PATH)
user_details = pd.read_csv(USER_DETAILS_PATH)


def home(request):
    return HttpResponse("Hi")

@csrf_exempt
def login(request):
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")

        filter = users["name"].isin([name])

        if filter.sum() > 0:
            real_password = users[filter]["password"].values.tolist()[0]
            if password == real_password:
                return HttpResponse(user_details[user_details["name"].isin([name])]["about"].values.tolist()[0])
            else:
                return HttpResponse("Incorrect password")
        else:
            return HttpResponse("Not an user")
    else:
        return HttpResponse("Incorrect Method")
