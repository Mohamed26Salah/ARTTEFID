def filter_list(lst, value):
    result = []
    for item in lst:
        if item.category == value:
            result.append(item)
    return result
import math
from NewRoomModel import *
import json
import numpy as np
# Opening JSON file
f = open('Room.json')

# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list
Room1 =Room.from_dict(data)
  
# Closing file
f.close()
from RoomModel import *
import json
# Opening JSON file
f = open('SampleData.json')

# returns JSON object as 
# a dictionary
data2 = json.load(f)
  
# Iterating through the json
# list
Room2 =RoomToBeUsed.from_dict(data2)
  
# Closing file
f.close()
wallsArray = filter_list(Room1.surfaces, 'wall')
wallsArray2=[[0 for elem in wallsArray],[0 for elem in wallsArray]]
for pos,Wall in enumerate(wallsArray):
    
    wallsArray2[0][pos]= [Wall.transform[12],Wall.transform[14]]
    
    wallsArray2[1][pos]= [Wall.scale.x,1]
    print(wallsArray2[1][pos])
