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


#if first 10 mins of market, uses as many data pts as possible
def ten_minute_average(table):
	for i in range(len(table)):
		if i==0:
			continue
		table[i][1] = float(table[i][1])
	for i in range(len(table)):
		if i==0:
			continue
		if i<11:
			sumsum = 0
			for j in range(i):
				sumsum += table[i-j][1]
			average = sumsum/i
			table[i][3] = average
		else:
			sumsum = 0
			for j in range(11):
				sumsum += table[i-j][1]
			average = sumsum/11
			table[i][3] = average
	return table

def ten_minute_standard_deviation(table):
	for i in range(len(table)):
		if i==0:
			table[i][2] = '10minStDev'
			continue
		if i<11:
			sumsum = 0
			for j in range(i):
				sumsum+= (float(table[i-j][1])-float(table[i-j][3]))**2
			variance = sumsum/i
			sd = variance**(1/2)
			table[i][2] = sd
		else:
			sumsum = 0
			for j in range(11):
				sumsum+= (float(table[i-j][1])-float(table[i-j][3]))**2
			variance = sumsum/11
			sd = variance**(1/2)
			table[i][2] = sd
	return table

#removes empty rows from the table and returns the updated table
def remove_empty_lines(talbe):
	newTable = []
	for row in table:
		if row != []:
			newTable += [row]
	return newTable


#returns table with data from csv file
def read(file_path):
	with open(file_path, 'r') as file:
		reader = csv.reader(file, dialect = 'excel')
		table = list(reader)
		file.close()
	return table

def write(file_path,table):
	with open(file_path, 'w') as file:
		writer = csv.writer(file, dialect = 'excel')
		writer.writerows(table)
		file.close()


if __name__ == '__main__':

	for i in range(560-544+1):
		try:
			file_name = '2024-06-20_' + str(544+i) + '.0strike.csv'
			file_path = '2024-06-20/' + file_name
			table = read(file_path)
			newTable = remove_empty_lines(table)
			write(file_path,newTable)
		except FileNotFoundError as e:
			continue

	file_path = '2024-06-20/2024-06-20_SPY.csv'
	table = read(file_path)
	newTable = remove_empty_lines(table)
	write(file_path,newTable)

	for i in range(556-523+1):
		try:
			file_name = '2024-06-21_' + str(523+i) + '.0strike.csv'
			file_path = '2024-06-21/' + file_name
			table = read(file_path)
			newTable = remove_empty_lines(table)
			write(file_path,newTable)
		except FileNotFoundError as e:
			continue

	file_path = '2024-06-21/2024-06-21_SPY.csv'
	table = read(file_path)
	newTable = remove_empty_lines(table)
	write(file_path,newTable)




'''
	file_path1 = '2024-06-06/2024-06-06_SPY copy.csv'
	table = read(file_path1)
	
	table = ten_minute_average(table)
	table = ten_minute_standard_deviation(table)

	file_path2 = '2024-06-06/2024-06-06_SPY.csv'
	write(file_path2,table)
'''

'''
newtable = []
	for i in range(len(table)):
		array = [table[i][0],table[i][1]]
		newtable += [array]
	for i in range(len(table)):
		if i==0:
			newtable[i]+= ['10minSD', '10minAverage']
		else:
			newtable[i]+= [0,0]
		newtable[i] += [table[i][3],table[i][4]]
	
	file_path2 = '2024-06-05/2024-06-05_SPY.csv'
	write(file_path2,newtable)
'''




