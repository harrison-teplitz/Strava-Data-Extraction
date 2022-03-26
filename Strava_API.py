import requests
import certifi
import urllib3
import mysql.connector

#import polyline
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#?client_id=77863&client_secret=62afc003e4dea79c0ea4e94afa95bb1753764f04&refresh_token=f46192646ed9c2b2f4577c58ab3452bf317e6517&grant_type=refresh_token

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

## Example Activity
##{'resource_state': 2, 'athlete': {'id': 38916511, 'resource_state': 1}, 'name': 'Evening Run', 'distance': 5758.9, 'moving_time': 2137, 'elapsed_time': 2512, 'total_elevation_gain': 48.3, 'type': 'Run', 'workout_type': None, 'id': 6845749570, 
# 'start_date': '2022-03-19T01:28:58Z', 'start_date_local': '2022-03-18T18:28:58Z', 'timezone': '(GMT-08:00) America/Los_Angeles', 'utc_offset': -25200.0, 'location_city': None, 'location_state': None, 'location_country': None,
#  'achievement_count': 5, 'kudos_count': 17, 'comment_count': 0, 'athlete_count': 1, 'photo_count': 0, 'map': {'id': 'a6845749570', 
# 'summary_polyline': 'mmecFfz`hVp@u@t@Ej@FKOYEQMC]@[CQq@FUAIEW[SKiABy@Fk@Ae@NWD{CCu@DL@XECAqAL{A?s@EmAAeC[fA@@EIEsA?m@JY@_@CcB]g@As@B_@EOB', 'resource_state': 2}, 'trainer': False, 'commute': False, 'manual': False, 'private': False,
#  'visibility': 'everyone', 'flagged': False, 'gear_id': 'g8185620', 'start_latlng': [37.38855357281864, -122.07027758471668], 'end_latlng': [37.386656161397696, -122.07000324502587], 'start_latitude': 37.38855357281864, 'start_longitude': -122.07000324502587,
#  'average_speed': 2.695, 'max_speed': 4.814, 'average_cadence': 77.1, 'has_heartrate': True, 'average_heartrate': 149.3, 'max_heartrate': 175.0, 'heartrate_opt_out': False, 'display_hide_heartrate_option': True, 'elev_high': 33.5, 'elev_low': 8.4, 'upload_id': 7282736224,
#  'upload_id_str': '7282736224', 'external_id': '2022-03-18-182851-Running-Harrison?s Apple?Watch.fit', 'from_accepted_tag': False, 'pr_count': 0, 'total_photo_count': 0, 'has_kudoed': False, 'suffer_score': 53.0}

#Connecting to mySQL server
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "harrison",
    database = 'StravaDB'
    )

#Create Cursor Instance
my_cursor = mydb.cursor()

#Create Database
def create_mySQL_DB(DB_name):
    comand = "CREATE DATABASE " + DB_name
    my_cursor.execute(comand)
#create_mySQL_DB('StravaDB') ----> only done once at the beginning

#Clear data in table if get_kudos() is ran again
my_cursor.execute('DELETE FROM activities')
my_cursor.execute('DELETE FROM followers')

#Create Table 
def create_mySQL_table():
    my_cursor.execute("""CREATE TABLE activities (name VARCHAR(255), date VARCHAR(255),
    type VARCHAR(255), distance INTEGER(10), activityID VARCHAR(255))""")
    my_cursor.execute("CREATE TABLE followers (name VARCHAR(255), kudos INTEGER(10))")
#create_mySQL_table() ##----> only done once at the beginning


#my_cursor.execute('ALTER TABLE activities MODIFY activityID VARCHAR(255)')
def get_kudos(x):
    header = {'Authorization': 'Bearer ' + access_token}
    param_a = {'per_page': x, 'page': 1} ## Parameter dictionary for getting activites. X = number of activites to see starting Last In First Out
    my_dataset = requests.get(activites_url, headers=header, params=param_a).json()
    #poly = my_dataset[0]["map"]["summary_polyline"]
    kudos_by_id = {}
    kudos_by_user = {}
    for i in range(len(my_dataset)):
        id = str(my_dataset[i]['id'])
        name = my_dataset[i]['name']
        date = my_dataset[i]['start_date']
        type_act = my_dataset[i]['type']
        distance = my_dataset[i]['distance']
        sql_code = "INSERT INTO activities (name, date, type, distance, activityID) VALUES (%s, %s, %s, %s, %s)"
        my_cursor.execute(sql_code, (name, date, type_act, distance, id))
        param_k = {'per_page': 30, 'page': 1}
        kudos_url = "https://www.strava.com/api/v3/activities/{}/kudos?page=&per_page=".format(str(id))
        kudos = requests.get(kudos_url, headers=header, params=param_k).json()
        kudo_list = []
        for dict in kudos:
            user = str(dict['firstname'])+'_' +str(dict['lastname'])
            kudo_list.append(user)
            if user in kudos_by_user.keys():
                kudos_by_user[user] += 1
            else:
                kudos_by_user[user] = 0
            #print(dict['firstname'],'gave kudos on', date, 'for this activity:', name)
        kudos_by_id[id] = kudo_list
    #sort python list "kudos_by_user.item()"
    sort_users = sorted(kudos_by_user.items(), key=lambda x: x[1], reverse=True)
    for i in sort_users[0:10]:
        #print(i[0], i[1])
        user = i[0]
        kudos = i[1]
        #sql_code = "INSERT INTO followers (name, kudos) VALUES (%s, %s)"
        my_cursor.execute("INSERT INTO followers (name, kudos) VALUES (%s, %s)", (user, kudos))
    mydb.commit()


get_kudos(15)
