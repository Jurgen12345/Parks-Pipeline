import requests


url ="https://msde630.class-labs.com/auth/me" 
headers = {"accept":"application/json", "X-Api-Key":"yourAPIKEY"}



r = requests.get(url=url, headers=headers)

if r.status_code == 200:
    print(r.text) 
elif r.status_code == 401:
    print("Not Authenticated. Please enter the correct api key.")