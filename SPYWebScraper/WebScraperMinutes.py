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

def extract_stock_price(html):
    soup = BeautifulSoup(html, 'html.parser')
    price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    if price_tag:
        return price_tag.text
    return None

def extract_stock_info(html):
    #info= [timeOfDay, price, change, %change, volume]

    currentTime = time.time()
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time

    soup1 = BeautifulSoup(html, 'html.parser')
    soup = soup1.find('main')
    price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    change_tag = soup.find('fin-streamer', {'data-field': 'regularMarketChange'})
    changePercent_tag = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'})
    price = price_tag.text
    change = change_tag.text
    percentChange = changePercent_tag.text
    
    container = soup.find('fin-streamer', {'data-field': 'regularMarketVolume'})
    if container:
        vol = container.text
    else:
        vol = '--'

    info = [time_of_day, price, change, percentChange, vol]
    return info

'''    container = soup.find('div', class_='container svelte-mgkamr')
    rows = container.find_all('fin-streamer')
    price_tag = rows[0]
    price_change = rows[1]
    percent_change = rows[2]
''' 


#returns dictionary with all options info -- keys are strike prices, elements are arrays:
# [lastPrice, bidCall, askCall, change, %change, Volume, OpenInterest impliedVolatility, STRIKE, lastPrice, bidPut, askPut, change, %change, impliedVolatility,]
def extract_options_prices(html):
    currentTime = time.time() - 15*60
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time

    soup = BeautifulSoup(html, 'html.parser')
    current_price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    if current_price_tag:
        current_price = float(current_price_tag.text.replace(',', ''))
        container = soup.find('section', {'data-testid': 'options-list-table'})
        containerTables = container.find_all('div')
        callTable = containerTables[1].find_all('table')
        putTable = containerTables[4].find_all('table')

        newDict = {}
        call_table = callTable[0]
        if call_table:
            callRows = call_table.find_all('tr')
            for row in callRows[1:]:  # Skipping header row
                cells = row.find_all('td')
                strike_price = float(cells[2].text.replace(',', ''))
                if abs(strike_price - current_price) <= current_price*0.02:
                    newDict[strike_price] = [cells[3].text, cells[4].text, cells[5].text, cells[6].text, cells[7].text,cells[8].text, cells[9].text, cells[10].text, strike_price, time_of_day]
       
        #array = newDict.keys()
        put_table = putTable[0]
        if put_table:
            putRows = put_table.find_all('tr')
            for row in putRows[1:]:
                cells = row.find_all('td')
                strike_price = float(cells[2].text.replace(',', ''))
                if abs(strike_price - current_price) <= current_price*0.02:
                    if strike_price in newDict:
                        newDict[strike_price] += [cells[3].text, cells[4].text, cells[5].text, cells[6].text, cells[7].text, cells[8].text, cells[9].text, cells[10].text]
       #                 array.remove(key)
                    else:
                        newDict[strike_price] = ['-','-','-','-','-','-','-','-', strike_price, cells[3].text, cells[4].text, cells[5].text, cells[6].text, cells[7].text, cells[8].text, cells[9].text, cells[10].text]
       # for i in range(len(list)):
       #     newDict[list[i]] += ['-','-','-','-','-','-','-','-']
        return newDict

#updates strike sheets and returns the new arrayOfStrikes
def strike_sheets(html, arrayOfStrikes):
    today = str(date.today())

    dictionary = extract_options_prices(html)
    keys = dictionary.keys()
    
   #filename should be 'today-key_strike.csv' 
   #path to the file should be 'today/filename'
    for key in keys:
        filename = today + '_'+ str(key) +'strike.csv'
        if key in arrayOfStrikes:
            add(filename, dictionary.get(key))
        else:
            write(filename, dictionary.get(key))
            arrayOfStrikes += [key]
    return arrayOfStrikes



def write(fileName, row):
    today = str(date.today())
    folder_path = today
    file_path = os.path.join(folder_path, fileName)
    with open(file_path, 'w') as file:
        writer = csv.writer(file, dialect='excel')
        fields = ['lastPrice', 'bidCall', 'askCall', 'change', '%change', 'Volume', 'OpenInterest', 'impliedVolatility', 'STRIKE', 'TIME', 'lastPrice', 'bidPut', 'askPut', 'change', '%change', 'Volume', 'OpenInterest', 'impliedVolatility']
        writer.writerow(fields)
        writer.writerow(row)
        file.close()

def add(fileName, row):
    file_path = today +'/'+fileName
    with open(file_path, 'a') as file:
        writer = csv.writer(file, dialect = 'excel')
        writer.writerow(row)
        file.close()

def timeArray():
    currentTime = time.time()
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time
    arr = time_of_day.split(':')
    for i in range(len(arr)):
        arr[i] = int(arr[i])
    return arr

if __name__ == "__main__":
    
    today = str(date.today())

    #makes the folder for today's files
    dir = rf"{today}"
    if not os.path.exists(dir):
        os.mkdir(dir)

    #sets current time
    currentTime = time.time()
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time
    arr = time_of_day.split(':')
    for i in range(len(arr)):
        arr[i] = int(arr[i])
    hour = int(time_of_day[0:2])

    #sets the necessary links
    optionsURL = "https://finance.yahoo.com/quote/SPY/options/?straddle=false"
    stockDayTable = [['TimeOfDay', 'Price', 'Change', '%Change', 'Volume']]
    stockURL = "https://finance.yahoo.com/quote/SPY/"

    #initializes empty list of strike prices with sheets
    arrayOfStrikes = []

    #while hour < 16:
    count = 0
    tick=0
    start = time.time()

#TIMER TO START AT 9:30AM
    endTime = '09:30:00'
    end = endTime.split(':')
    for i in range(len(end)):
        end[i] = int(end[i])
    curr = timeArray()
    start = time.time()
    waitTime = (end[0]-curr[0])*60*60 + (end[1]-curr[1])*60 + (end[2]-curr[2])
    end = start + waitTime

    while time.time() < end:
        time.sleep(end-time.time())        #TIMER TO START AT 9:30AM ends

#WHILE LOOP UPDATES OPTIONS CSVs AND COLLECTS DATA FOR UNDERLYING (to update after market closes)
    while arr[0] < 16:
        array = []
        options_content = fetch_html(optionsURL)
        stock_content = fetch_html(stockURL)

        if options_content:
            try:
                try:
                    stock_info = extract_stock_info(stock_content)
                except TypeError as e:
                    print('TypeError occured, so a URL error may have occured')
                    stock_info = ['--','--','--','--','--']
            except AttributeError as e:
                try:
                    print("yahoo hates your IP")
                    stock_info = extract_stock_info(options_content)
                except AttributeError as e:
                    print(f"yahoo really hates your IP, you only got {count} iterations")
                    stock_info = ['--','--','--','--','--']
                    break
        stockDayTable += [stock_info]

        try:
            arrayOfStrikes = strike_sheets(options_content, arrayOfStrikes)
        except TypeError as e:
            print('TypeError occured, so a URL error may have occured')
            continue

        tick += 1
        count +=1
        if tick == 20:
            print(count)
            tick=0
        currentTime = time.time()
        local_time = time.localtime(currentTime)
        time_of_day = time.strftime("%H:%M:%S", local_time)  #current time
        arr = time_of_day.split(':')
        for i in range(len(arr)):
            arr[i] = int(arr[i])
        time.sleep(60-1.72857001)  # Wait for X seconds before fetching the data again


#write Stock csv File
    stockcsvName = today + '_SPY.csv'

    today = str(date.today())
    folder_path = today
    file_path = os.path.join(folder_path, stockcsvName)

    with open(file_path, 'w') as SPY:
        writer = csv.writer(SPY, dialect='excel')
        writer.writerows(stockDayTable)
        SPY.close()
    print(time.time()-start, ' seconds')
    print((time.time()-start)/60, 'minutes')
    print(((time.time()-start)/60)/60, 'hours')
    print(count, ' iterations')

           # dictionary = extract_options_prices(html_content)













