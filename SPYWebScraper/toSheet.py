import csv
from datetime import date

import time
import os
import os.path
import csv



def write(fileName):
	with open(fileName, 'w') as testFile:
		writer = csv.writer(testFile, dialect='excel')
		fields = ["time", "rowNumber", "50"]
		rows = []
		for i in range(20):
			currentTime = time.time()
			local_time = time.localtime(currentTime)
			time_of_day = time.strftime("%H:%M:%S", local_time)
			rows += [[time_of_day, i+1, "50"]]
		writer.writerow(fields)
		writer.writerows(rows)
		testFile.close()

def add(fileName):
	with open(fileName, 'a') as testFile:
		writer = csv.writer(testFile, dialect='excel')
		fields = ["time", "rowNumber", "50"]
		rows = []
		for i in range(20):
			currentTime = time.time()
			local_time = time.localtime(currentTime)
			time_of_day = time.strftime("%H:%M:%S", local_time)
			rows += [[time_of_day, i+1, "50"]]
		writer.writerow(fields)
		writer.writerows(rows)
		testFile.close()

def read(fileName):
	with open(fileName, 'r') as testFile:
		reader = csv.reader(testFile)
		for row in reader:
			print(listToStringcommas(row))

def listToStringcommas(array):
	word = ''
	for i in range(len(array)):
		word += str(array[i]) + ","
	word = word[0:-1]
	return word


#VERY IMPORTANT ** this method reads each line of the csv file as an array
# the listToStringcommas() function will convert the array to a string with 
# elements separated by commas, no comma at the end.

#returns array with integer values [HH,MM,SS]
def timeArray():
    currentTime = time.time()
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time
    arr = time_of_day.split(':')
    for i in range(len(arr)):
        arr[i] = int(arr[i])
    return arr

def TOD():
    currentTime = time.time()
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time
    return time_of_day

#end time should be written as 'HH:MM:SS'
#returns True when end time is reached.
def timer(endTime):
	end = endTime.split(':')
	for i in range(len(end)):
		end[i] = int(end[i])
	curr = timeArray()
	start = time.time()
	waitTime = (end[0]-curr[0])*60*60 + (end[1]-curr[1])*60 + (end[2]-curr[2])
	end = start + waitTime

	while time.time() < end:
		time.sleep(end-time.time())
	return True

if __name__ == "__main__":
	float('--')











