from __future__ import print_function
import codecs
import json

from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
import math
from pymavlink import mavutil
from waypoint import WayPoint

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Demonstrates basic mission operations.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None

cords=[]

# Home 17.435813547717206, 78.54114926739005
lat=17.39702935952299
long=78.49029276520014

#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default(lat=lat,lon=long)
    connection_string = sitl.connection_string()

JSON_PATH=""

# Connect to the Vehicle
print('GCS:Connecting to vehicle on:  %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)




def validate_json():
    f=open('sample.json')
    try:
        data=json.load(f)
        f.close()
        return data
    except ValueError:
        print("JSON Invalid Error")
        exit()
    except FileNotFoundError:
        print("JSON does not exist")
        exit()
    
            

def parse_json(data):
    waypointList=[]
    for waypoint in data:
        waypointList.append(WayPoint(float(waypoint["latitude"]),float(waypoint["longitude"]),int(waypoint["index"])))
        cords.append((float(waypoint["latitude"]),float(waypoint["longitude"])))
    return waypointList

    
def create_mission(waypoints):
    cmds = vehicle.commands

    print("GCS:Clear any existing commands")
    cmds.clear() 
    
    print("GCS:Define/add new commands.")
    # Add new commands. The meaning/order of the parameters is documented in the Command class. 
     
    initialAltitude=10.0
    #Add MAV_CMD_NAV_TAKEOFF command. This is ignored if the vehicle is already in the air.
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, initialAltitude))
    
    for waypoint in waypoints:
        newcmd=Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 10, 0, 0, 0, waypoint.lat, waypoint.long, initialAltitude)
        cmds.add(newcmd)
    
    # add a dummy twaypoint n+1 at n to let us know we have reached destination 
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, waypoints[-1].lat, waypoints[-1].long, initialAltitude-1))
        
    print("GCS:Uploading new commands to vehicle")
    cmds.upload()
        
    
    
    

def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5



def download_mission():
    """
    Download the current mission from the vehicle.
    """
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready() # wait until download is complete.


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("GCS:Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print("GCS:Waiting for vehicle to initialise...")
        time.sleep(1)

        
    print("GCS:Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:      
        print("GCS:Waiting for arming...")
        time.sleep(1)

    print("GCS:Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude
    

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print("GCS:Altitude: ", vehicle.location.global_relative_frame.alt)      
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            print("GCS:Reached target altitude")
            break
        time.sleep(1)



# Validate the JSON File
print('GCS:Validating JSON')
data=validate_json()

# Sort the JSON 
print('GCS:Sorting JSON by waypoint order')
data = sorted(data, key=lambda d: d['index'])

n_points=len(data)
print(*data)



# Parsing the JSON file for Waypoints 
print('GCS:Parsing JSON and adding waypoints')
waypoints =parse_json(data)

# Create a new mission from the parsed waypoints 
create_mission(waypoints)

# Arm the Drone and Take Off with to a specified altitiude
print('GCS:Starting to Arm')
altitude=10
arm_and_takeoff(altitude)


print("GCS:Starting mission")
# Reset mission set to first (0) waypoint
vehicle.commands.next=0

# Set mode to AUTO to start mission
vehicle.mode = VehicleMode("AUTO")

x = 0


@vehicle.on_message(['WAYPOINT_CURRENT', 'MISSION_CURRENT'])
def listener(self, name, m):
    global x
    if m.seq > x:
        print("Taking a picture")
        x += 1
    

cords=set(cords)

# Mission Monitoring 
while True:
    nextwaypoint=vehicle.commands.next
    print('GCS:Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint()))
    
    if (vehicle.location.global_frame.lat,vehicle.location.global_frame.lon) in cords:
        print("hehe")
    
  
    if nextwaypoint==n_points+1: #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
        print("Exit 'standard' mission when start heading to final waypoint (5)")
        break
    time.sleep(1)

print('GCS:Return to launch')
vehicle.mode = VehicleMode("RTL")


#Close vehicle object before exiting script
print("GCS:Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    print("GCS:Shutting down simulator")
    sitl.stop()
