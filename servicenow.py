import requests
import json

def make_request(detections,filename):
   
    #API URL to Access Incident Table
    url = 'https://dev74772.service-now.com/api/now/v1/table/incident'

    # Eg. User name="admin", Password="admin" for this code sample.
    user = 'aes.creator'
    pwd = 'QoB$cRTgv/17'

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    # Do the HTTP request
    response = requests.post(url, auth=(user, pwd), headers=headers ,data=json.dumps({"short_description":filename+" "+str(detections)}))

    # Check for HTTP codes other than 200
    #print(response.status_code);
    if response.status_code < 200: 
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()

    # Decode the JSON response into a dictionary and use the data
    data = response.json()
    print(data["result"])

