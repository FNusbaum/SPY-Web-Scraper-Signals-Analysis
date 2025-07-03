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

#retrieves html data from a url to be deciphered using Beautiful Soup
def fetch_html(url):
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        request = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Encoding': 'gzip'
        })
        with urlopen(request, context=context) as response:
            if response.info().get('Content-Encoding') == 'gzip':
                buf = BytesIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                html_bytes = f.read()
            else:
                html_bytes = response.read()
            html = html_bytes.decode("utf-8")
            return html
    except HTTPError as e:
        print(f"HTTP error occurred: {e.code} {e.reason}")
    except URLError as e:
        print(f"URL error occurred: {e.reason}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    return None



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
def num_UV_fractal(table, time, k, metric):
    numRanges = 0
    numUp=0
    numDown=0
    followedBykup = 0
    followedBykdown = 0
    for i in range(len(table)-time-1):
        if i==0:
            continue
        for j in range(time-1):
            if abs(table[i+j+1][0] - table[i+j][0] - 60) > 4:
                continue
        #now we know we have a range of time values that are 1 minute apart each.
        oddEven = 0
        if time % 2 ==1:
            oddEven = 1
        num = math.floor(time/2)
        firstUP = range_up(table, i, i+num)
        secondUP = range_down(table, i+num+oddEven, i+time)
        firstDOWN = range_down(table,i,i+num)
        secondDOWN = range_up(table,i+num+oddEven,i+time)
        if firstUP and secondUP:
            numRanges +=1
            numUp+=1
         #   print(i, ', ', time, ', up')
            if followedUPby(k,table, i+time, metric):
                followedBykup +=1

        if firstDOWN and secondDOWN:
            numRanges +=1
            numDown+=1
          #  print(i, ', ', time, ', down')
            if followedDOWNby(k,table, i+time, metric):
                followedBykdown +=1
    try:
        percentUp = round(followedBykup/numUp*100)
    except ZeroDivisionError as e:
        percentUp=0
    try:
        percentDown = round(followedBykdown/numDown*100)
    except ZeroDivisionError as e:
        percentDown=0
    result = (f'{time} minutes: {numUp} up, {numDown} down, {numRanges} total\n %followed up {k} = {percentUp}%; %followed down {k} = {percentDown}%\n')
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
    
    #file_path = '2024-06-05/2024-06-05_SPY.csv'
    #file_path = '2024-06-06/2024-06-06_SPY.csv'
    #file_path = '2024-06-07/2024-06-07_SPY.csv'
    file_path = '2024-06-14/2024-06-14_SPY.csv'
    table = injest_file(file_path)
    table = time_to_seconds(table)
    for i in range(8):
        num = num_UV_fractal(table, i+3, 3, 0)
        print(num)
    #num = num_UV_fractal(table, 4)
    #print(num)







