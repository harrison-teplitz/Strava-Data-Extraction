import requests
import certifi
import urllib3
import xml.etree.ElementTree as ET

#import polyline
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

## URLs for talking to Strava API
auth_url = "https://www.strava.com/oauth/token"
activites_url = 'https://www.strava.com/api/v3/athlete/activities'
kudos_url = "https://www.strava.com/api/v3/activities/77863/kudos"

## This payload is used to take my refresh token and recieve an access token
payload = {
    'client_id': "77863",
    'client_secret': '62afc003e4dea79c0ea4e94afa95bb1753764f04',
    'refresh_token': 'f46192646ed9c2b2f4577c58ab3452bf317e6517',
    'grant_type': "refresh_token",
    'f': 'json'
}
#print("Requesting Token...\n")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
#print('access token = {}\n'.format(access_token))

header = {'Authorization': 'Bearer ' + access_token}
param_a = {'per_page': 10, 'page': 1} ## Parameter dictionary for getting activites. X = number of activites to see starting Last In First Out
my_dataset = requests.get(activites_url, headers=header, params=param_a).json()
athlete_id = str(my_dataset[0]['athlete']['id'])

routes_url = "https://www.strava.com/api/v3/athletes/{}/routes?page=&per_page=".format(str(athlete_id))

param_r = {'per_page': 1, 'page': 1}
routes = requests.get(routes_url, headers=header, params=param_r).json()
route_id = routes[0]['id']

def get_gpx(route_id):
    gpx_url = "https://www.strava.com/api/v3/routes/{}/export_gpx".format(str(route_id))
    route_gpx = requests.get(gpx_url, headers=header)
    route = str(route_gpx.content)
    route = route.replace('\\n', '')
    #print(route)
    with open('route_gpx.gpx', "w") as f:
        f.write(route)
    #tree = ElementTree.fromstring(route_gpx.content)
    #print(tree)

get_gpx(route_id)
