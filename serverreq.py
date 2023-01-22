import requests

SERVER_URL="http://18.234.187.114:4000/image/upload/addall"


def update_flight(body):
    try:
        response=requests.post(SERVER_URL,json=body)
        if(response.status_code==200):
            print("Images Updatad Successfully")
    except:
        print("Some error occured")
        
    
    
    