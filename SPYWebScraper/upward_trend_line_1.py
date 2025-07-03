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


#creates potential upward trend line from index1 through index 2
#returns [slope, y_intercept] for line, where price at 0 index is the y intercept.
def line_of_best_fit(table, index1, index2):
	price1 = float(table[index1][1])
	price2 = float(table[index2][1])
	slope = (price2-price1)/(index2-index1)
	y_intercept = price1 - slope*index1
	return [slope, y_intercept]

#quality of the line of best fit
#index2 is the second index of the line
#line is the ouput of line_of_best_fit function
#array_of_stalactites is the list of indeces with prices to compare the line to
def line_deviation(table, index2, line, array_of_salactites):
	deviation =0
	num = 0
	for i in range(len(array_of_salactites)):
		if array_of_salactites[i]<index2:
			continue
		index = array_of_salactites[i]
		price = float(table[index][1])
		line_price = line[0]*index + line[1]
		deviation += (line_price-price)**2
		num +=1
	deviation = deviation/num
	deviation = deviation**(1/2)
	return deviation


#how often is there a point, whose neighbors are both 1 sd above?
def list_of_stalactites(table):
	array = []
	for i in range(len(table)-4):
		if i<3:
			continue
		price = float(table[i][1])
		prev1 = float(table[i-1][1])
		prev2 = float(table[i-2][1])
		if i>3:
			prev3 = float(table[i-3][1])
		if i>4:
			prev4 = float(table[i-4][1])
			post4 = float(table[i+4][1])
		post1 = float(table[i+1][1])
		post2 = float(table[i+2][1])
		post3 = float(table[i+3][1])

		n=10
		average=0
		if i<11:
			for j in range(i-1):
				average += float(table[i-j-1][1])
			for j in range(10):
				average += float(table[i+j+1][1])
			average = average/(i+10)
		if i> len(table)-11:
			for j in range(len(table)-i-1):
				average += float(table[i+j+1][1])
			for j in range(10):
				average += float(table[i-j-1][1])
			average = average/(i+10)
		if i>10 and i<len(table)-11:
			for j in range(n):
				average += float(table[i+j+1][1])
				average += float(table[i-j-1][1])
			average = average/(2*n)
		if price >average:
			continue
		if i<=3:
			if price < prev1 and price < prev2 and price < post1 and price < post2 and price < post3 and price < post4:
				array+=[i-1]
				continue
		if i>3:
			if price < prev1 and price < prev2 and price < prev3 and price < post1 and price < post2 and price < post3 and price < prev4 and price < post4:
				array+=[i-1]
		else:
			if price < prev1 and price < prev2 and price < prev3 and price < post1 and price < post2 and price < post3:
				array += [i-1]
	return array


'''
	num = 0
	array = []
	for i in range(len(table)-3):
		if i<4:
			continue
		price = table[i][1]
		average = (float(table[i-3][1])+float(table[i-2][1])+float(table[i-1][1])+float(table[i+1][1])+float(table[i+2][1])+float(table[i+3][1]))/6
		if left_check(table,i) and right_check(table,i):
			#print(i, ':  av - price = ', average-float(table[i][1]), " (sd-(av-pr))/sd = ", (float(table[i][2]) + (average-float(table[i][1])))/float(table[i][2]))
			num+=1
			array+=[i]
	return array
'''

def left_check(table, index):
	price = float(table[index][1])
	sd = float(table[index][2])
	previous1 = float(table[index-1][1])
	previous2 = float(table[index-2][1])
	previous3 = float(table[index-3][1])
	if price<previous1 and price<previous2 and price<previous3:
		print(index)
		return True
	#if price +sd/10 >previous1 and price +sd/5 >previous2:
	#	return False
	else:
		return False

def right_check(table, index):
	price = float(table[index][1])
	sd = float(table[index][2])
	previous1 = float(table[index+1][1])
	previous2 = float(table[index+2][1])
	previous3 = float(table[index+3][1])
	if price<previous1 and price<previous2 and price<previous3:
		print(index)
		return True
	#if price +sd/10 >previous1 and price +sd/5 >previous2:
	#	return False
	else:
		return False

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
	file_path1 = '2024-06-20/2024-06-20_SPY.csv'
	data = injest_file(file_path1)
	times = select_times(data)
	prices = select_prices(data)

	table = read(file_path1)
	array = list_of_stalactites(table)
	colors = []
	for i in range(len(times)):
		if i in array:
			colors += ['red']
		else:
			colors += ['blue']
	for i in range(len(array)-1):
		for j in range(len(array)-i):
			if j==0:
				continue
			if array[j+i]-array[i] <=70:
				numPoints = 0
				for k in range(len(array)):
					if array[k] > array[i+j]:
						numPoints+=1
				ld = line_deviation(table, array[j+i], line_of_best_fit(table,array[i],array[j+i]), array)
				if ld <1 and numPoints > len(array)*.2:
					time = (f'{table[array[i]][0]}-{table[array[i+j]][0]}')
					first = table[array[i]][0].split(':')
					second = table[array[i+j]][0].split(':')
					for p in range(3):
						first[p] = int(first[p])
						second[p] = int(second[p])
					t1 = first[0]*60 + first[1] - 9*60 -30
					t2 = second[0]*60 + second[1] - 9*60 -30
					time = (f'{t1}-{t2}')
					print(ld, ', time:', time,  ', points:', numPoints)
	print(array)
	print(len(array))

	plt.scatter(times, prices, s=2, color = colors)
	#plt.scatter(times, stalactite_prices, s=1, color = 'green')
	plt.xlabel('times')
	plt.ylabel('SPY price')
	plt.title('06-14')
	plt.show()


	#THE PROBLEM IS THAT IT'S MISSING KEY STALACTITES. YOU NEED TO CHANGE HOW IT FINDS STALACTITES
	#ALSO, LINE_DEVIATION IS WACK, MAYBE ONLY HAVE IT LOOK AT CERTAIN MOMENTS FOR CALCULATION?






