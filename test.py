import requests
import json

#TEST FOR AUTHENTICATION

authenticate_url = "http://localhost:5000/authenticate"

#(POSITIVE)
r = requests.post(url = authenticate_url, headers={'Content-Type':'application/json'}, data = json.dumps({"username":"admin@admin.com", "password":"password"}))

try:
    print(r.status_code)
    print("Login(POSITIVE) Test Successful")
except:
    print("Login(POSITIVE) Test Unsuccessful")

#(NEGETIVE)
r = requests.post(url = authenticate_url, headers={'Content-Type':'application/json'}, data = json.dumps({"username":"admin@admin.com", "password":"wrongpassword"}))

try:
    print(r.status_code)
    print("Login(NEGETIVE) Test Successful")
except:
    print("Login(NEGETIVE) Test Unsuccessful")

#TEST FOR QUIZ LIST

quiz_list_url = "http://localhost:5000/quiz-categories?id=1"

r = requests.get(url = quiz_list_url)
try:
    print(r.status_code)
    print("QUIZ LIST Test Successful")
except:
    print("QUIZ LIST Test Unsuccessful")
