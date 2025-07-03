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
import matplotlib.pyplot as plt




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

def select_prices(table):
    array = []
    for i in range(len(table)):
        if i == 0:
            continue
        array +=[float(table[i][1])]
    return array

def select_times(table):
    array = []
    for i in range(len(table)):
        if i==0:
            continue
        array+= [i-1]
    return array


if __name__ == '__main__':
    file_path4 = '2024-06-20/2024-06-20_SPY.csv'
    data = injest_file(file_path4)
    times = select_times(data)
    prices = select_prices(data)
    plt.scatter(times, prices, s=1)
    plt.xlabel('times')
    plt.ylabel('SPY price')
    plt.title('06-14')

    plt.show()







