#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import tweepy

import json
import csv

import folium
from folium import plugins

#Twitter API access details
consumer_key = "******"
consumer_secret = "******"
access_token = "******"
access_secret = "******"


#Create CSV file to Write coordinates to
csv_File = open("tweet_Coords.csv", "w") # use "a" if using alternative version
csv_File.write("Long,Lat, Text\n") #header for CSV file
#csv_File.close() #when using alternative version 

#Record complete JSON
#json_File = open('/Output/tweets_All.json', 'w')
json_File = open('tweets_All.json', 'w')

#Amount of time you want to run data collection in seconds
end_time = time.time() + 60 #seconds

#If you want to collect a certain number of tweets use the count version
#count = 0


###############################################################################
###################CREATE TWITTER LISTENER AND COLLECT TWEETS##################
###############################################################################

class listener(tweepy.StreamListener):

    def on_data(self, data):
        
        #global count
        #if count <= 10: #to collect 10 tweets

        while time.time() <= end_time:
            
            json_data = json.loads(data)
            json.dump(json_data, json_File)            
            
            coords = json_data["coordinates"]
            text = json_data["text"]
            #hashtags = json_data["hashtags"]
            
            if coords is not None:
               print(coords["coordinates"], text)
               lon = coords["coordinates"][0]
               lat = coords["coordinates"][1]
               
               csv_File.write(str(lon) + ",")
               csv_File.write(str(lat) + ",")
               csv_File.write(
                       str(text.lower().replace(',', '_').replace('\n','_').strip()) + "\n")
               
               
               #alternative way, write to file and close so progress is saved
               #in case there is an error, the csv progress up to point will
               #be saved
               #
               #with open("tweet_Coords.csv", "a") as tweetfile:
               #    tweetfile.write(str(lon) + "," + str(lat) + "," + \
               #    str(text.lower().replace(',', '_').replace('\n','_').strip()) + "\n")
               

               #count += 1 #use if you are doing count version
               
            return True
        
        else:
            csv_File.close()
            json_File.close()
            return False

    def on_error(self, status):
        print(status)


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
twitterStream = tweepy.Stream(auth, listener())



#To collect tweets by a location, use locations = [bounding coordinates]
#London
#twitterStream.filter(locations = [-0.468905,51.286142,0.121350,51.681241])
#US
twitterStream.filter(locations = [-124.145554,25.378667,-66.53325,49.204841])

#To collect tweets by specific terms use filter(track = 'string')
#twitterStream.filter(track = ['data science', 'data', 'insight'])

#To Combine, separate with comma (note it's an OR relationship)
#twitterStream.filter(track = ['vote', 'election', 'elections'], \
#                     locations = [-124.145554,25.378667,-66.53325,49.204841])





###############################################################################
############CREATE FILES NEEDED FOR MAPPING FROM COLLECTED TWEETS##############
###############################################################################




terms = ['vote', 'election', 'elections', 'primary', 'democrat', 'dnc', 'primaries' \
         'political', 'primarias', 'primaria', 'republican', 'presidential', 'congress'\
         'biden', 'sanders', 'warren', 'bloomberg', 'gabbard', 'candidate', \
         'super tuesday', 'ballot', 'democracy', 'elect', 'trueblue']


location_List = []


with open('tweet_Coords.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    header = next(reader, None) #exclude header from read
    
    #create list of coordinates relating to search terms
    #folium takes in a list as argument
    for row in reader:
        for term in terms:
            if term in row[2]: #filter through tweets
                location_List.append([float(row[1]), float(row[0])])
                


#Center of map cretaed by folium
us_Center_Coords = [39.300299, -95.667875] #US coordinates to create map lat/long
lon_Center_Coords = [51.518935, -0.122075] #London coordinates to create map



###############################################################################
########################SECTION TO CREATE HEATMAP##############################
###############################################################################
    
hm = plugins.HeatMap(location_List, radius=20)

heatmap = folium.Map(location=us_Center_Coords, zoom_start=4,
                     tiles='cartodbpositron', width=840, height=560)

heatmap.add_child(hm)                      

heatmap.save('heatmap.html')

        

###############################################################################
########################SECTION TO CREATE POINTMAP#############################
######EXAMPLE OF COFFEE RELATED TWEETS AND STARBUCKS LOCATIONS IN LONDON#######
###############################################################################


sb_Locations = []   #Starbucks locations
coffee_Tweets = []  #Tweets related to coffee
#sb_Tweets = []      #Tweets related to Starbucks 

#Read in Starbucks locations from CSV into a list
with open('./input/SB_Locations.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    header = next(reader, None) #exclude header from read
    for row in reader:
        sb_Locations.append([float(row[0]), float(row[1])])


#From the collected tweets, read in the coordinates of rows that
#are related to either the keyword 'coffee' or 'starbucks'
with open('./input/Twitter.csv', 'r', encoding='Latin-1') as csvFile:
    reader = csv.reader(csvFile)
    header = next(reader, None) #exclude header from read
    #coord_list = list(reader)    

    for row in reader:
        if "starbucks" in row[2] or "coffee" in row[2]:
            coffee_Tweets.append([float(row[0]), float(row[1])])
        else:
            pass

#Create map with folium     
map_Lon = folium.Map(location=lon_Center_Coords, zoom_start=12,
                     tiles='cartodbpositron', width=840, height=560)



#Create folium method to add coordinates to map.    
def add_2Map(coord_List, color):
    [folium.CircleMarker(coord_List[i], radius=3, #list comprehension way of doing
                color=color, fill_color=color, #fill=True, fill_opacity = 0.8
                ).add_to(map_Lon) 
                for i in range(len(coord_List))]
    
   
#Add locations to map using the above created method     
add_2Map(sb_Locations, '#008000') #Add Starbucks locations to map in green 
add_2Map(coffee_Tweets, '#FF0000') #Add location of Tweets in red
#add_2Map(sb_Tweets, '#0000FF')


#Save Map   
map_Lon.save('point_Map.html')