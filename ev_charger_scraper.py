import json
import time
import requests
import pandas as pd
import geopandas as gpd

#Read PC4 file in order to create centroid points to loop over
pc4 = gpd.read_file('GIS\PC4_2020_NL.shp')
df = gpd.GeoDataFrame(data=pc4['PC4'], geometry=pc4['geometry'].centroid).to_crs(4326)

coord_list = [(x,y) for x,y in zip(df['geometry'].x , df['geometry'].y)]

#Initial Parameters
keywords = "ev charger" #Search term in Google Maps
api_key = "" #Insert Google Maps API key

final_data = []
count = 0

for a in coord_list:

    coordinate = str(a[1])+"%2C"+str(a[0])
    #Pulls data from Google Maps based on coordinate grid and pushes data into final_data list final_data = []for coordinate in coordinates:   
    #The radius of extraction can be adjusted in the link
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={coordinate}&radius=15000&keyword={keywords}&key={api_key}"   
    
    while True:     
        print(url)      
        respon = requests.get(url)          
        jj = json.loads(respon.text)        
        results = jj['results']   
        for result in results:          
            name = result['name']          
            place_id = result ['place_id']          
            lat = result['geometry']['location']['lat']          
            lng = result['geometry']['location']['lng']             
            rating = result['rating']          
            types = result['types']          
            vicinity = result['vicinity']          
            business_status = result['business_status']            
            data = [name, place_id, lat, lng, rating, types, vicinity, business_status]          
            final_data.append(data)           

            time.sleep(1) 

        if 'next_page_token' not in jj:    
                break   
        else:           
                url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={jj['next_page_token']}&key={api_key}"

    print(str(count)+' done')
    count +=1
    time.sleep(5)

#Generated data is parsed into a Dataframe form
labels = ['Place Name','Place ID', 'Latitude', 'Longitude', 'na', 'Types', 'Vicinity', 'Business Status']
ev_df = pd.DataFrame.from_records(final_data,columns=labels)

#Drop duplicate rows since PC4 searches overlap
ev_clean_df = ev_df.drop_duplicates(subset="Place ID")

ev_clean_df.to_csv('')

#Create GeoDF using lat, lon to create Point features
gdf = gpd.GeoDataFrame(ev_clean_df, geometry=gpd.points_from_xy(ev_clean_df.Longitude, ev_clean_df.Latitude))
gdf.drop('Types', axis=1, inplace=True)
gdf.to_file('', type='GPKG')