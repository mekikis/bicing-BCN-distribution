import pandas as pd
import geopandas as gpd
import requests
import json
import time
import matplotlib.pyplot as plt
from shapely.geometry import shape, Point
import warnings
warnings.filterwarnings("ignore")


# settings to show the whole table in the console (debugging purposes)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 11)
pd.set_option('display.width', 1000)
for replay in range(400):
    # site to download the dataset
    url = "https://www.bicing.barcelona/es/get-stations"
    r = requests.get(url)
    stations_json = json.loads(r.content.decode())
    with open('stations.json', 'w') as json_file:
        json.dump(stations_json['stations'], json_file)

    # read the json dataset of the bicing stations with panda
    df = pd.read_json(r'stations.json')
    # concatenate street name with street number
    df['street'] = df['streetName'] + ' ' + df['streetNumber']
    # choose only active stations
    df = df[df.status == 1]
    # drop useless columns
    stations = df.drop(['type', 'icon', 'transition_start', 'transition_end', 'streetName', 'streetNumber', 'type_bicing', 'status', 'disponibilidad', 'electrical_bikes','mechanical_bikes'], axis=1)

    # reset the index of the stations dataframe
    stations = stations.reset_index(drop=True)
    # print(stations)

    # set the filepath and load in a shapefile
    fp = 'shape_dense.geojson'

    map_df = gpd.read_file(fp)
    # create new column that defines the map color
    map_df['bike_sum'] = pd.Series([0 for x in range(len(map_df.index))], index=map_df.index)

    # choose only the polygons and the bike_sum columns for the final map
    map_df = map_df[['geometry', 'bike_sum']]

    # # count stations in a polygon
    for idx, i in enumerate(map_df.geometry):
        poly = shape(i)
        for counter in range(len(stations)):
            # print(stations.longitude[counter], stations.latitude[counter])
            point = Point(stations.longitude[counter], stations.latitude[counter])
            if poly.contains(point):
                map_df.bike_sum[idx] = min(100, map_df.bike_sum[idx] + stations.bikes[counter])

    vmin, vmax = 0, 100
    fig, ax = plt.subplots(1, figsize=(10, 6))
    # Create colorbar as a legend
    sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    # empty array for the data range
    sm._A = []
    # add the colorbar to the figure
    cbar = fig.colorbar(sm)
    ax.set_title('Number of bicycles per neighborhood', fontdict={'fontsize': '18', 'fontweight' : '3'})
    ax.annotate('Source: Barcelona Bicing Database, '+str(time.ctime()), xy=(0.1, .08),  xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=10, color='#555555')
    ax.axis('off')
    map_df.plot(column='bike_sum', cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8')
    fig.savefig('Figures/status_'+str(int(time.time())))
    plt.close(fig)
    print(map_df.bike_sum.max())
    time.sleep(5*60-2)

