import ssl
import certifi
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import gzip
from io import BytesIO
from bs4 import BeautifulSoup
import time
import csv
from datetime import date
import os
import os.path
import math

def injest_file(file_path):
    table = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file, dialect = 'excel')
        table = list(reader)
        file.close()
    for i in range(len(table)-1):
        row = table[i+1]
        for j in range(len(row)):
            try:
                row[j] = float(row[j])
            except ValueError as e:
                row[j]=row[j]
    return table

def injest_files(file_paths_array):
    table = []
    for i in range(len(file_paths_array)):
    	file_path = file_paths_array[i]
    	with open(file_path, 'r') as file:
	        reader = csv.reader(file, dialect = 'excel')
	        newtable = list(reader)
	        if i !=0:
	        	newtable.pop(0)
	        table += newtable
	        file.close()

    for i in range(len(table)-1):
    	row = table[i+1]
    	for j in range(len(row)):
            try:
                row[j] = float(row[j])
            except ValueError as e:
                row[j]=row[j]
    return table


#turns the time of day values into seconds (integers)
def time_to_seconds(table):
    for i in range(len(table)-1):
        row = table[i+1]
        timearray = row[0].split(':')
        for i in range(3):
            timearray[i] = int(timearray[i])
        time = timearray[0]*60*60 + timearray[1]*60+timearray[0]
        row[0] = time

    return table


#determines the number of U or V fractals represented in the table
#fractal takes place over a specified amount of time (minutes)
#metric is 0 or 1, and denotes how we want to consider "followed by" (monotonically or start/end points?)
#metric = 1 is monotonic, metric = 0 looks only at start and end points.

#NEED TO MODIFY TO SEARCH FOR ASYMMETRIC FRACTALS
#if underlying up for n mins, down for m mins, find P(up for/in k mins) (start with m,k=1)

def num_Asymetric_UV_fractal(table, TimeUp, TimeDown, TimeFollow, metric):
    numRanges = 0
    up_by_Time_Follow = 0
    TotalTime = TimeUp + TimeDown
    for i in range(len(table)-TotalTime-1):
        if i==0:
            continue
        for j in range(TotalTime-1):
            if abs(table[i+j+1][0] - table[i+j][0] - 60) > 4:
                continue
        #now we know we have a range of time values that are 1 minute apart each.


        Rise = range_up(table, i, i+TimeUp)
        Fall = range_down(table, i+TimeUp, i+TotalTime)

        if Rise and Fall:
            numRanges +=1
         #   print(i, ', ', time, ', up')
            if followedUPby(TimeFollow,table, i+TotalTime, metric):
                up_by_Time_Follow +=1


    try:
        PercentBackUp = round(up_by_Time_Follow/numRanges*100)
    except ZeroDivisionError as e:
        PercentBackUp = 0
    
    if metric == 1:
    	difficulty = 'monotonically by'
    else:
    	difficulty = 'after'
    if numRanges !=0:
        result = (f'{TimeUp} min up, {TimeDown} min down: {numRanges} total, {PercentBackUp}% up {difficulty} {TimeFollow} min')
    else:
        result = (f'{TimeUp} min up, {TimeDown} min down: {numRanges} total')
    return result

def range_up(table, start, end):
    result = True
    for i in range(end-start):
        row1 = table[start+i]
        row2 = table[start+i+1]
        if row2[1]-row1[1] < 0:
            result=False
            break
    return result

def range_down(table, start, end):
    result = True
    for i in range(end-start):
        row1 = table[start+i]
        row2 = table[start+i+1]
        if row2[1]-row1[1] > 0:
            result = False
            break
    return result

#k is TimeFollow, i is start+TotalTime
def followedUPby(k, table, i, metric):
    if metric == 0:    
        row1 = table[i]
        try:
            row2 = table[i+k]
        except IndexError as e:
            return False
        if row2[1]-row1[1] <0:
            return False
        return True
    else:
        result = True
        for j in range(k):
            row1 = table[i+j]
            try:
                row2 = table[i+j+1]
            except IndexError as e:
                result = False
                break
            if row2[1]-row1[1] <0:
                result = False
                break
        return result


def followedDOWNby(k, table, i, metric):
    if metric == 0:    
        row1 = table[i]
        try:
            row2 = table[i+k]
        except IndexError as e:
            return False
        if row2[1]-row1[1] >0:
            return False
        return True
    else:
        result = True
        for j in range(k):
            row1 = table[i+j]
            try:
                row2 = table[i+j+1]
            except IndexError as e:
                result = False
                break
            if row2[1]-row1[1] >0:
                result = False
                break
        return result




if __name__ == "__main__":
    
    file_path1 = '2024-06-05/2024-06-05_SPY.csv'
    file_path2 = '2024-06-06/2024-06-06_SPY.csv'
    file_path3 = '2024-06-07/2024-06-07_SPY.csv'
    file_path4 = '2024-06-14/2024-06-14_SPY.csv'
    file_path5 = '2024-06-18/2024-06-18_SPY.csv'
    file_path6 = '2024-06-20/2024-06-20_SPY.csv'
    file_path7 = '2024-06-21/2024-06-21_SPY.csv'
    array = [file_path1,file_path2, file_path3, file_path4, file_path5,file_path6,file_path7]
    table1 = injest_files(array)
    table2 = injest_file(file_path7)
    table = time_to_seconds(table1)
    for i in range(9):
    	if i<3:
    		continue
    	print('')
    	for j in range(i):
    		#num_Asymetric_UV_fractal(table, TimeUp, TimeDown, TimeFollow, metric)
        	num = num_Asymetric_UV_fractal(table, i, 0+j, 1, 0)
        	print(num)
    #num = num_Asymetric_UV_fractal(table, 4)
    #print(num)


    #metric is 0 or 1, and denotes how we want to consider "followed by" (monotonically or start/end points?)
    #metric = 1 is monotonic, metric = 0 looks only at start and end points.







