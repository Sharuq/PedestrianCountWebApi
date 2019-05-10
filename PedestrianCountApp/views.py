
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

def PedestrianCount(request,sensorId):
    try:
        """Requesting pedestrian count API call and store data to dataframe"""
        request = requests.get("https://data.melbourne.vic.gov.au/resource/d6mv-s43h.json")
        pedestrianSensorDetials = request.content.decode("utf-8")
        data = json.loads(pedestrianSensorDetials)
        df = pd.DataFrame(data)

        """Grouping results based on sensors latest time"""
        group = df.groupby('sensor_id', as_index=False).agg({
            'time': 'max'
        })

        """Storing results to list"""
        maxValueDic = group.to_dict('index')
        maxValueList = []
        for key, value in maxValueDic.items():
            maxValueList.append(value)

        """Creating a dataframe with filtered sensor id"""
        appended_data = []
        for item in maxValueList:
            df3 = df.loc[(df['time'] == item['time']) & (df['sensor_id'] == item['sensor_id'])]
            appended_data.append(df3)
        finalDF = pd.concat(appended_data)
        finalDF = finalDF.reset_index(drop=True)
        finalDF['sensor_id'] = finalDF['sensor_id'].astype('str')

        """Getting record  for the input sensor id"""
        finalDic = finalDF.to_dict('index')
        result=getSensorDetails(str(sensorId),finalDic)

        """Returning json result"""
        return JsonResponse(result,safe=False)
    except ValueError as e:
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)

def getSensorDetails(id,finalDic):
    for key, value in finalDic.items():
        if value['sensor_id'] == id:
            result = value
            break
    return result