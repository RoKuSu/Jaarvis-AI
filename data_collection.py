# #!/usr/bin/env python3
#
# import http.client
#
# conn = http.client.HTTPSConnection("api-int.reachnowtechnology.com")
#
# headers = {
#     "x-api-key": "HVwoCnH9G97h2mnvuHebM5xCdukHxq2b4ePWbhP8",
#     'content-type': "application/json",
#     'cache-control': "no-cache",
#     'postman-token': "80abe64d-ee46-6ea8-4454-1bf9261b0384"
#     }
#
# conn.request("GET", "/v1/vehicles",{},headers)
#
# res = conn.getresponse()
# data = res.read()
#
# print(res.status,res.reason,data)

import requests
import json
import time
import os.path

url = "http://api-int.reachnowtechnology.com/v1/vehicles"

headers = {
    'x-api-key': "HVwoCnH9G97h2mnvuHebM5xCdukHxq2b4ePWbhP8",
    'cache-control': "no-cache",
    'postman-token': "58c20aee-9ce5-35e9-d355-71b3eaf97c33"
    }

response = requests.request("GET", url, data={}, headers=headers)

i=0
while True:
    with open(os.path.join("data_collected/",'output'+str(i)+'.txt'),'w') as current:
        current.write(response.text)
    i+=1
    print(i," file written")
    time.sleep(300)
