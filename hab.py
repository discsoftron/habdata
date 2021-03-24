#!/usr/bin/env python3

# This program allows a hab client to submit data with an HTTP GET request.  Additionally, web clients can view the 
# most recent data from the hab clients.

from flask import Flask, render_template, session, request, jsonify
import datetime, csv, os.path, requests
from collections import defaultdict

# Initialize variables
logFile = "habLog.csv"

# Check if the log file exists.  If it doesn't, create it.
if not os.path.isfile(logFile):
    open(logFile, 'a').close()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

@app.route('/')
def index():
    
    # Create a list of valid clientIDs
    # Read whole log file
    logLines = []
    
    with open(logFile, 'r') as fd:
        reader = csv.reader(fd, delimiter=',')
        for row in reader:
            logLines.append(row)
    fd.close()
    
    # Create a list of unique ClientIDs
    # [item[0] for item in logLines] gives a list of the first element of each log line
    # set() returns the unique values in a list and list() creates a list from those elements
    uniqueIDs = list(set([item[0] for item in logLines]))
    mostRecents = []
    recentClientDates = {}
    for uniqueID in uniqueIDs:
        # Find the index of the list occurence of the uniqueID in logList
        firstIndex = (len([item[0] for item in logLines]) - 1 - [item[0] for item in logLines][::-1].index(uniqueID))
        # Add the data to the most recents list
        mostRecents.append({"clientID": logLines[firstIndex][0], "date": logLines[firstIndex][1], "time": logLines[firstIndex][2], "insideTemp": logLines[firstIndex][3], "outsideTemp": logLines[firstIndex][4], "pressure": logLines[firstIndex][5], "batteryVoltage": logLines[firstIndex][6], "solarVoltage": logLines[firstIndex][7], "signal": logLines[firstIndex][8], "altitude": logLines[firstIndex][9]}) 
        recentClientDates[uniqueID] = logLines[firstIndex][1] + " " + logLines[firstIndex][2]
    
    # Create a dictionary of data of each client's last 24 hours of data
    nowtime = datetime.datetime.now().replace(microsecond=0)
    habData = defaultdict(list)
    for uniqueID in uniqueIDs:
        recentClientDate = datetime.datetime.strptime(recentClientDates[uniqueID], "%Y-%m-%d %H:%M:%S")
        for clientLine in logLines:
            if clientLine[0] == uniqueID:
               logDate =  datetime.datetime.strptime(clientLine[1] + ' ' + clientLine[2], "%Y-%m-%d %H:%M:%S")
               if (recentClientDate - logDate).total_seconds() < 86400: # 86400 is the number of seconds in 24 hours
                   # Add client data
                   habData[uniqueID].append({"date": str(logDate), "insideTemp": clientLine[3], "outsideTemp": clientLine[4], "pressure": clientLine[5], "batteryVoltage": clientLine[6], "solarVoltage": clientLine[7], "signal": clientLine[8], "altitude": clientLine[9]})
    
    # Create dataset for temperature of a specific client
    clientID = "Gabe"
    timeLabels = []
    clientTemps = []
    clientPressure = []
    for clientLine in logLines:
        if clientLine[0] == clientID:
            timeLabels.append(clientLine[1] + ' ' + clientLine[2])
            clientTemps.append(clientLine[3])
            clientPressure.append(clientLine[5])
    
    return render_template('index.html', habInfo=mostRecents, habData = dict(habData), clientIDs=uniqueIDs)

@app.route('/postData', methods=['GET'])
def postData():
    
    # Process the posted data and write it to a csv log file.
    
    clientID = request.args.get('clientID', None)
    temp1 = request.args.get('temp1', None)
    temp2 = request.args.get('temp2', None)
    pressure = float(request.args.get('pressure', None))/100.0
    volt1 = request.args.get('volt1', None)
    volt2 = request.args.get('volt2', None)
    signal = request.args.get('signal', None)
    alt = request.args.get('alt', None)
    
    # If the altitude wasn't sent, calculate it
    
    if alt is None:
    
        # Get the barometric pressure at sea level for the area (KGON) from weather.gov and convert to hPa
        weatherApi = requests.get('https://api.weather.gov/stations/KGON/observations/latest')
        seaLevelPressure = weatherApi.json()['properties']['seaLevelPressure']['value'] / 100.0
        print ("seaLevelPressure: " + str(seaLevelPressure))
        
        # Calculate altitude with hypsometric formula
        alt = (((seaLevelPressure / pressure)**(1/5.257) - 1) * (float(temp1) + 273.15)) / 0.0065
        alt = round(alt, 1)
        
    
    nowtime = datetime.datetime.now().replace(microsecond=0)
    (date,time) = str(nowtime).split(" ")
    # Prepend a zero to the hour or minute if needed
    #hour = str(nowtime.hour)
    #if (len(hour) == 1):
    #    hour = "0" + hour
        
    #minute = str(nowtime.minute)
    #if (len(minute) == 1):
    #    minute = "0" + minute
        
    #time = hour + ":" + minute
    #date = nowtime.date()
    
    # Append log entry to text file
    logRow = [clientID, date, time, temp1, temp2, pressure, volt1, volt2, signal, alt]
    
    with open(logFile, 'a') as fd:
        writer = csv.writer(fd)
        writer.writerow(logRow)
    fd.close()
    
    return render_template('success.html')

@app.route('/getData', methods=['GET'])
def getData():
    
    # API for returning clients and data
    
    # Create a list of valid clientIDs
    # Read whole log file
    logLines = []
    
    with open(logFile, 'r') as fd:
        reader = csv.reader(fd, delimiter=',')
        for row in reader:
            logLines.append(row)
    fd.close()
    
    # Create a list of unique ClientIDs
    # [item[0] for item in logLines] gives a list of the first element of each log line
    # set() returns the unique values in a list and list() creates a list from those elements
    uniqueIDs = list(set([item[0] for item in logLines]))
    mostRecents = []
    for uniqueID in uniqueIDs:
        # Find the index of the list occurence of the uniqueID in logList
        firstIndex = (len([item[0] for item in logLines]) - 1 - [item[0] for item in logLines][::-1].index(uniqueID))
        
        # Add the data to the most recents list
        
        mostRecents.append({"clientID": logLines[firstIndex][0], "date": logLines[firstIndex][1], "time": logLines[firstIndex][2], "insideTemp": logLines[firstIndex][3], "outsideTemp": logLines[firstIndex][4], "pressure": logLines[firstIndex][5], "batteryVoltage": logLines[firstIndex][6], "solarVoltage": logLines[firstIndex][7], "signal": logLines[firstIndex][8], "altitude": logLines[firstIndex][9]}) 
    
    return jsonify(mostRecents)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5001,debug=False)
