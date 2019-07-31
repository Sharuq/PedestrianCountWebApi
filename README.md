# Django Pedestrian Count Web API

A RESTFUL API processes the city of Melbourne real time pedestrian counts from Pedestrian Counting System - Past Hour (counts per minute)
and the predicted hourly pedestrain count data from stored in Firebase database. The API processess the datasets into a  required format.

OPEN API's used:

Pedestrian Counting System - Past Hour (counts per minute) - https://data.melbourne.vic.gov.au/Transport-Movement/Pedestrian-Counting-System-Past-Hour-counts-per-mi/d6mv-s43h

Pedestrian Counting System – 2009 to Present (counts per hour) - https://data.melbourne.vic.gov.au/Transport-Movement/Pedestrian-Counting-System-2009-to-Present-counts-/b2ak-trbp

Check out the API hosted on heroku webserver on below link( *Change Sensor ID's [1-50] in url to check*)

http://pedestriancountwebapi.herokuapp.com/combinedpedestriancount/12/
