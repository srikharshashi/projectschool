from yolov5 import detect 
import os


# Make request to Service Now
def make_request(imgpath):
    print("Making a request in servicenow for img ",imgpath)
    # 11092002;12:34:basketballcourt.jpeg
    # {
    #    "date"
    #    "time"
    #     "location" 
    # }

# Input Image Size
imgsz=(3904,5184)

# Confidence Thershold
conf_threshold=0.6

# Custom Weights
weights='C:\\Users\\dasoj\\OneDrive\\Desktop\\drone\\yolov5\\bestweights\\best.pt'

# Labels in text file
save_txt=True

# Save confidence in text file
save_conf=True

# bounding box thickness
line_thickness=3

# minimum number of trash items to be considered to be added to dataset
trash_count=10

#GPU Number 
cuda_device=0

# Image Source
source="C:\\Users\\dasoj\\OneDrive\\Desktop\\drone\\images"

# Check if all packages are installed for YOLO
detect.check_requirements(exclude=('tensorboard', 'thop'))

# Run prediction using YOLO and the above mentioned parameters
predicted_list= detect.run(imgsz=imgsz,device=cuda_device,conf_thres=conf_threshold,weights=weights,save_txt=save_txt,save_conf=save_conf,line_thickness=line_thickness,source=source)

# get all the predicted images and 
for prediction in predicted_list:
    if(prediction["n_labels"]>trash_count):
        imgpath=os.getcwd()+"\\yolov5\\"+prediction['img_path']
        make_request(imgpath=imgpath)
        
