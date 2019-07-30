
from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
import requests
import json
import pandas as pd
from firebase import firebase
from datetime import datetime, timedelta
from sodapy import Socrata
import pytz
import datetime


"""Updated Web Api"""

# Getting real time latest pedestrain counts readings and processing it
## sid: sensor id

def getRealTimeLatestCount(sid):
    dic = {}
    client = Socrata("data.melbourne.vic.gov.au", None)
    results = client.get("d6mv-s43h")
    rt_df = pd.DataFrame.from_records(results)

    rt_df = rt_df.drop(['direction_1', 'direction_2'], 1)
    rt_df['date_time'] = pd.to_datetime(rt_df['date_time'])

    latest_df = rt_df.iloc[rt_df.groupby(['sensor_id']).apply(lambda x: x['date_time'].idxmax())]
    latest_df.reset_index(drop=True, inplace=True)

    latest_json = json.loads(latest_df.to_json(orient='columns'))
    rowid = list(latest_json['sensor_id'].keys())[list(latest_json['sensor_id'].values()).index(str(int(sid)))]
    dic['real_time'] = latest_json['time'][rowid]
    dic['total_of_directions'] = latest_json['total_of_directions'][rowid]
    return dic


# Getting stored predicted pedestrain hourly counts from Firebase database and processing to required format

def getPredictedHourlyCount(month, day, hour, minute, sid):
    from firebase import firebase
    authentication = firebase.FirebaseAuthentication('eb:ae:e6:5b:e6:b2:ff:db:1c:89:28:ff:b0:7b:cc:b6:eb:a7:97:6f',
                                                     'cpen0004@student.monash.edu', True, True)
    firebase.authentication = authentication
    user = authentication.get_user()

    if month < 10:
        month = 'm0' + str(month)
    else:
        month = 'm' + str(month)

    if day < 10:
        day = 'd0' + str(day)
    else:
        day = 'd' + str(day)

    if minute >= 45:
        time = hour + 1
    else:
        time = hour

    if time < 10:
        time = 't0' + str(time)
    else:
        time = 't' + str(time)

    firebase = firebase.FirebaseApplication('https://nightwalker-59e4e.firebaseio.com/', None)
    result = firebase.get('/count_prediction_structure/' + month + '/' + day + '/' + time + '/s' + str(int(sid)), '0')

    return result
	
#Final combined required format 
def CombinedPedestrianCount(request,sensorId):
    try:
        current_time = datetime.datetime.now(pytz.timezone('Australia/Sydney'))
        predicted = getPredictedHourlyCount(current_time.month, current_time.day, current_time.hour, current_time.minute, str(sensorId))
        real_time = getRealTimeLatestCount(str(sensorId))
        combinedResult = dict(predicted, **real_time)
        combinedResult['predict_time'] = combinedResult.pop('time')

        if current_time.minute >= 45:
            timeCheck = current_time.hour + 1
            oneHourTimeCheck = current_time.hour + 2
        else:
            timeCheck = current_time.hour
            oneHourTimeCheck = current_time.hour + 1

        combinedResult['predict_time'] = str(timeCheck) + ":00 - " + str(oneHourTimeCheck) + ":00"


        """Returning json result"""
        return JsonResponse(combinedResult, safe=False)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)
