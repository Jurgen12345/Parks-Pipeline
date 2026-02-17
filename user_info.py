import requests


url ="https://msde630.class-labs.com/auth/me" 
headers = {"accept":"application/json", "X-Api-Key":"parks_sk_jqAC9bnQiNTnO9hEmHg6_6qH_7kxjdhl6UoI_zIdlMY"}



r = requests.get(url=url, headers=headers)

if r.status_code == 200:
    print(r.text) 
elif r.status_code == 401:
    print("Not Authenticated. Please enter the correct api key.")