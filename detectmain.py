from yolov5 import detect 
import os
from uploadimg import upload_file
from servicenow import make_request
from serverreq import update_flight
import datetime

# This script takes in the flightId and detects the trash in the given images 
# Once it does that it uploads all the images to amazon S3 and adds the image urls to Flight in server



flight_id=input("Enter a Flight ID ")

# Input Image Size
imgsz=(3904,5184)

# Confidence Thershold
conf_threshold=0.6

# Custom Weights
weights=os.getcwd()+'\\yolov5\\bestweights\\best.pt'

# Labels in text file
save_txt=True

# Save confidence in text file
save_conf=True

# bounding box thickness
line_thickness=3

# minimum number of trash items to be considered to be added to dataset
trash_count=3

#GPU Number 
cuda_device=0

# Image Source
source=os.getcwd()+"\\images"

# Check if all packages are installed for YOLO
detect.check_requirements(exclude=('tensorboard', 'thop'))

# Run prediction using YOLO and the above mentioned parameters
predicted_list= detect.run(imgsz=imgsz,device=cuda_device,conf_thres=conf_threshold,weights=weights,save_txt=save_txt,save_conf=save_conf,line_thickness=line_thickness,source=source)

request_body=[]

count =0

# get all the predicted images and 
for prediction in predicted_list:
    if(prediction["n_labels"]>trash_count):
        print("Uploading File",count," and making a request to service now")
        imgpath=os.getcwd()+"\\"+prediction['img_path']
        imgurl=upload_file(flightid=flight_id,file_path=imgpath)
        body={
            "flight_id":flight_id,
            "date":str(datetime.datetime.now()),
            "detect":prediction["n_labels"],
            "main_url":imgurl
        }
        request_body.append(body)
        print("Making a request in ServiceNow")
        make_request(prediction["n_labels"],os.path.basename(imgpath))
        print("Done for image",count)
        count+=1


# Make a request to sever to add images 
update_flight(body=request_body)

        

