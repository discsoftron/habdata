#!/usr/bin/env python3

# This program allows a hab client to submit data with an HTTP GET request.  Additionally, web clients can view the 
# most recent data from the hab clients.

from flask import Flask, render_template, session, request, jsonify
import datetime, csv, os.path

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
    for uniqueID in uniqueIDs:
        # Find the index of the list occurence of the uniqueID in logList
        firstIndex = (len([item[0] for item in logLines]) - 1 - [item[0] for item in logLines][::-1].index(uniqueID))
        # Add the data to the most recents list
        mostRecents.append({"clientID": logLines[firstIndex][0], "date": logLines[firstIndex][1], "time": logLines[firstIndex][2], "insideTemp": logLines[firstIndex][3], "outsideTemp": logLines[firstIndex][4], "pressure": logLines[firstIndex][5], "batteryVoltage": logLines[firstIndex][6], "solarVoltage": logLines[firstIndex][7]}) 
    
    # Create dataset for temperature of a specific client
    clientID = "TEST"
    timeLabels = []
    clientTemps = []
    clientPressure = []
    for clientLine in logLines:
        if clientLine[0] == clientID:
            timeLabels.append(clientLine[1] + ' ' + clientLine[2])
            clientTemps.append(clientLine[3])
            clientPressure.append(clientLine[5])
    
    return render_template('index.html', habInfo=mostRecents, timeLabels=timeLabels, clientTemps=clientTemps, clientPressure=clientPressure)

@app.route('/postData', methods=['GET'])
def postData():
    
    # Process the posted data and write it to a csv log file.
    
    clientID = request.args.get('clientID', None)
    temp1 = request.args.get('temp1', None)
    temp2 = request.args.get('temp2', None)
    pressure = request.args.get('pressure', None)
    volt1 = request.args.get('volt1', None)
    volt2 = request.args.get('volt2', None)
    
    nowtime = datetime.datetime.now().replace(microsecond=0)
    # Prepend a zero to the hour or minute if needed
    hour = str(nowtime.hour)
    if (len(hour) == 1):
        hour = "0" + hour
        
    minute = str(nowtime.minute)
    if (len(minute) == 1):
        minute = "0" + minute
        
    time = hour + ":" + minute
    date = nowtime.date()
    
    # Append log entry to text file
    logRow = [clientID, date, time, temp1, temp2, pressure, volt1, volt2]
    
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
        
        mostRecents.append({"clientID": logLines[firstIndex][0], "date": logLines[firstIndex][1], "time": logLines[firstIndex][2], "insideTemp": logLines[firstIndex][3], "outsideTemp": logLines[firstIndex][4], "pressure": logLines[firstIndex][5], "batteryVoltage": logLines[firstIndex][6], "solarVoltage": logLines[firstIndex][7]}) 
    
    return jsonify(mostRecents)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5001,debug=False)