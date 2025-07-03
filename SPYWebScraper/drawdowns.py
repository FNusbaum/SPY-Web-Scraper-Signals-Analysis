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

#table must have 
def drawdowns(table, depth)




if __name__ == '__main__':
	file_path1 = '2024-06-05/2024-06-05_SPY.csv'
    file_path2 = '2024-06-06/2024-06-06_SPY.csv'
    file_path3 = '2024-06-07/2024-06-07_SPY.csv'
    file_path4 = '2024-06-14/2024-06-14_SPY.csv'
    file_path5 = '2024-06-18/2024-06-18_SPY.csv'
    array = [file_path1,file_path2, file_path3, file_path4, file_path5]
    table1 = injest_files(array)
    table2 = injest_file(file_path5)
    table = time_to_seconds(table2)






