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

#takes only the stock price from the url, grabs the first one it finds
#must be careful that it grabs the right one
def extract_stock_price(html):
    soup = BeautifulSoup(html, 'html.parser')
    price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    if price_tag:
        return price_tag.text
    return None

#10bolinger is the signal (+/-1) developed from the bollinger band method
#10MA is the 10 minute moving average --> both 10 minute signals begin at 9:40am
#count+1 is numrows (including fields as a row)
def extract_stock_info(html, count, stockDayTable):
    #info= [timeOfDay, price, change, %change, volume]

    currentTime = time.time()
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time

    soup1 = BeautifulSoup(html, 'html.parser')
    soup = soup1.find('main')
    price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    price = float(price_tag.text.replace(',',''))
    container = soup.find('fin-streamer', {'data-field': 'regularMarketVolume'})
    if container:
        vol = container.text
    else:
        vol = '--'
    average = '--'
    Boll = '--'

    #we have data for the 10 minute moving
    numdata = len(stockDayTable)
    if numdata <11:
        average = 0
        for i in range(len(stockDayTable)-1):
            average += float(stockDayTable[i+1][1])
        average += float(price)
        average = average/numdata
    else:
        average = 0
        for i in range(10):
            average+= float(stockDayTable[-(i+1)][1])
        average += float(price)
        average = average/11
    #average done
    #SD
    if numdata <11:
        sd =0
        for i in range(len(stockDayTable)-1):
            sd += (float(stockDayTable[i+1][1])-average)**2
        sd += (float(price)-average)**2
        sd = sd/numdata
        sd = sd**(1/2)
    else:
        sd = 0
        for i in range(10):
            sd += (float(stockDayTable[-(i+1)][1])-average)**2
        sd += (float(price)-average)**2
        sd = sd/11
        sd = sd**(1/2)
    #SD done
    #Boll
    bollHigh = average + 2*sd
    bollLow = average -2*sd
    Boll = 0
    if float(price)>bollHigh:
        Boll = 1
    if float(price) < bollLow:
        Boll = -1
    #Boll done


    info = [time_of_day, float(price), sd, average, Boll, vol]
    return info


#10bolinger is the signal (+/-1) developed from the bollinger band method
#10MA is the 10 minute moving average --> both 10 minute signals begin at 9:40am
#count+1 is numrows (including fields as a row)
def extract_20second_stock_info(html, count, stock20seconds):
    #info= [timeOfDay, price, 10MA, 10Bollinger, volume]

    currentTime = time.time()
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time

    soup1 = BeautifulSoup(html, 'html.parser')
    soup = soup1.find('main')
    price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    price = price_tag.text
    container = soup.find('fin-streamer', {'data-field': 'regularMarketVolume'})
    if container:
        vol = container.text
    else:
        vol = '--'

    #average = '--'
    #Boll = '--'

    strength = RSI()

    info = [time_of_day, price, strength, vol]

    return info


def RSI():
    RSIurl = "https://finance.yahoo.com/quote/SPY/history/"
    #table = ['open', 'close'] 14x2
    RSI_content = fetch_html(RSIurl)
    soup = BeautifulSoup(RSI_content, 'html.parser')

    percentChange_tag = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'})
    
    if percentChange_tag:
        percentChange = percentChange_tag.text
        answer = percentChange[1:-2]
        answer2 = float(answer)*0.01
    else:
        return None
    currentLoss = 0
    currentGain = 0
    if answer2>0:
        currentGain = answer2
    if answer2<0:
        currentLoss = answer2

    info = []
    tableContainer = soup.find('table', class_='table svelte-ewueuo')
    table = tableContainer.find('tbody')
    rows = table.find_all('tr')
    for i in range(14):
        #1 = open, 4 = close
        cells = rows[i].find_all('td')
        openPrice = cells[1].text
        closePrice = cells[4].text
        row = [float(openPrice), float(closePrice)]
        info += [row]

    posNeg = []
    for i in range(14):
        if info[i][0]<info[i][1]:
            posNeg+=[-1]
        if info[i][0] > info[i][1]:
            posNeg+=[1]
        if info[i][0] == info[i][1]:
            posNeg+=[0]
    gainLoss = []
    for i in range(13):
        if posNeg[i]>0:
            gainLoss +=[max(0,(info[i][0]-info[i+1][1])/info[i+1][1])]
        if posNeg[i]<0:
            gainLoss +=[max(0,(-info[i][0]+info[i+1][1])/info[i+1][1])]
        if posNeg[i]==0:
            gainLoss += [0]
    gainSum=0
    lossSum=0
    for i in range(13):
        if posNeg[i]>0:
            gainSum += gainLoss[i]
        if posNeg[i]<0:
            lossSum += gainLoss[i]
    RSI = 100 - 100/(1 + (gainSum + currentGain)/(lossSum + currentLoss))
    #RSI = 100 - 100/(1+((totalGain + currentgain)/(totalLoss + currentloss)))
    return RSI



#returns dictionary with all options info -- keys are strike prices, elements are arrays:
# [lastPrice,bidCall,askCall,change,%change,Volume,OpenInterest,impliedVolatility,SPY,STRIKE,Time_Of_Day,lastPrice,bidPut,askPut,change,%change,Volume,OpenInterest,impliedVolatility]
def extract_options_prices(html, table):
    #subtract 15 minutes from the current time so that the options info is recorded correctly
    currentTime = time.time() - 15*60
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time

    soup = BeautifulSoup(html, 'html.parser')

    current_price = float(table[(len(table)-15)][1])

    container = soup.find('section', {'data-testid': 'options-list-table'})

    if container:
        containerTables = container.find_all('div')
        callTable = containerTables[1].find_all('table')
        putTable = containerTables[4].find_all('table')

        newDict = {}
        call_table = callTable[0]
        if call_table:
            callRows = call_table.find_all('tr')
            for row in callRows[1:]:  # Skipping header row
                cells = row.find_all('td')
                if cells:
                    strike_price = float(cells[2].text.replace(',', ''))
                    if abs(strike_price - current_price) <= current_price*0.02:
                        newDict[strike_price] = [cells[3].text, cells[4].text, cells[5].text, cells[6].text, cells[7].text,cells[8].text, cells[9].text, cells[10].text,current_price, strike_price, time_of_day]
                else:
                    return None
        #array = newDict.keys()
        put_table = putTable[0]
        if put_table:
            putRows = put_table.find_all('tr')
            for row in putRows[1:]:
                cells = row.find_all('td')
                if cells:
                    strike_price = float(cells[2].text.replace(',', ''))
                    if abs(strike_price - current_price) <= current_price*0.02:
                        if strike_price in newDict:
                            newDict[strike_price] += [cells[3].text, cells[4].text, cells[5].text, cells[6].text, cells[7].text, cells[8].text, cells[9].text, cells[10].text]
       #                    array.remove(key)
                        else:
                            newDict[strike_price] = ['-','-','-','-','-','-','-','-', strike_price, cells[3].text, cells[4].text, cells[5].text, cells[6].text, cells[7].text, cells[8].text, cells[9].text, cells[10].text]
                else:
                    return None
       # for i in range(len(list)):
       #     newDict[list[i]] += ['-','-','-','-','-','-','-','-']
        return newDict
    else:
        return None

#updates strike sheets and returns the new arrayOfStrikes
#calls extract_options_prices(), write(), add()
def strike_sheets(html, arrayOfStrikes, table):
    today = str(date.today())

    dictionary = extract_options_prices(html, table)
    if dictionary == None:
        return None
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
        fields = ['lastPrice', 'bidCall', 'askCall', 'change', '%change', 'Volume', 'OpenInterest', 'impliedVolatility','Underlying', 'STRIKE', 'TIME', 'lastPrice', 'bidPut', 'askPut', 'change', '%change', 'Volume', 'OpenInterest', 'impliedVolatility']
        writer.writerow(fields)
        writer.writerow(row)
        file.close()

def add(fileName, row):
    today = str(date.today())
    file_path = today +'/'+fileName
    with open(file_path, 'a') as file:
        writer = csv.writer(file, dialect = 'excel')
        writer.writerow(row)
        file.close()

def read(fileName, row):
    today = str(date.today())
    file_path = today +'/'+fileName
    with open(file_path, 'r') as file:
        reader = csv.reader(file, dialect = 'excel')
        writer.writerow(row)
        file.close()

#returns array with integer values [HH,MM,SS]
def timeArray():
    currentTime = time.time()
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time
    arr = time_of_day.split(':')
    for i in range(len(arr)):
        arr[i] = int(arr[i])
    return arr

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
    if time.time() < end:
        time.sleep(end-time.time())
    return True

#makes folder for the day
#scrapes options and stock URLs
#compiles CSV files for each strike price and one for the underlying
def scrape(optionsURL, stockURL):
    
    #makes the folder for today's files
    today = str(date.today())
    dir = rf"{today}"
    if not os.path.exists(dir):
        os.mkdir(dir)

    #initializes table for underlying csv file
    stockDayTable = [['TimeOfDay', 'Price', '10minSD', '10minAverage','Bollinger', 'Volume']]
    stockcsvName = today + '_SPY.csv'
    folder_path = today
    file_path = os.path.join(folder_path, stockcsvName)
    #write stock csv file
    with open(file_path, 'w') as SPY:
        writer = csv.writer(SPY, dialect='excel')
        writer.writerows(stockDayTable)
        SPY.close()


    #initializes empty list of strike prices to keep track of which strikes already have a csv file
    arrayOfStrikes = []

    #initialize counters and start time to keep track of how long function ran and number of iterations
    count = 0
    tick=0

    #tells the program sleep until 9:30am
    timer('9:30:00')      #start collecting data at 9:30 am
    start = time.time()
    arr = timeArray()

    #WHILE LOOP UPDATES OPTIONS CSVs AND COLLECTS DATA FOR UNDERLYING (to update after market closes)
    #loop ends at 4:00pm when the market closes
    while arr[0] <16 or arr[1]<30:
        loopBegin = time.time()
        #retrieves html contet
        options_content = fetch_html(optionsURL)
        stock_content = fetch_html(stockURL)

        #retrieves stock information and adds it to stockDayTable (to be compiled into csv after market closes)
        if arr[0]<16:
            if options_content:
                filename = today + '_20secDetail.csv'
                indicator = 0
                try:
                    try:
                        stock_info = extract_stock_info(stock_content, count, stockDayTable)
                    except TypeError as e:
                        print('TypeError occured, so a URL error may have occured')
                        indicator = 1
                except AttributeError as e:
                    try:
                        print("yahoo hates your IP")
                        stock_info = extract_stock_info(stock_content, count, stockDayTable)
                    except AttributeError as e:
                        print(f"yahoo really hates your IP, you only got {count} iterations")
                        indicator = 1
                        break
                if indicator == 0:
                    stockDayTable += [stock_info]
                    stockcsvName = today + '_SPY.csv'
                    folder_path = today
                    file_path = os.path.join(folder_path, stockcsvName)
                    with open(file_path, 'a') as SPY:
                        writer = csv.writer(SPY, dialect='excel')
                        writer.writerow(stock_info)
                        SPY.close()


        #retireves options information and adds a new row to each strike's csv file
        #if (arr[0] >=10 or arr[1]>45):
        if count >=15:
        #if (arr[0] >=10 or arr[1]>45):
            try:
                arrayOfStrikesTEMP = strike_sheets(options_content, arrayOfStrikes, stockDayTable)
                if arrayOfStrikesTEMP == None:
                    print('strike sheets returned None')
                else:
                    arrayOfStrikes = arrayOfStrikesTEMP
            except TypeError as e:
                print('TypeError occured, so a URL error may have occured')

        #prints the number of iterations completed every 20 iterations, just so we know something's happening
        tick += 1
        count +=1
        if tick == 5:
            print(count, " iterations")
            tick=0

        loopEnd = time.time()
        runTime = loopEnd-loopBegin
        #sleeps while loop for a minute so that we get one data dump close to every 60 seconds
        time.sleep(60-runTime)  # Wait for X seconds before fetching the data again
        #20-1.72857001)
        #updates current time so the loop knows when to end
        arr = timeArray()
   

    #print time elapsed in seconds, minutes, hours, and number of iterations (rows)
    print(time.time()-start, ' seconds')
    print((time.time()-start)/60, 'minutes')
    print(((time.time()-start)/60)/60, 'hours')
    print(count, ' iterations')

    #SCRAPING FINISHED


if __name__ == "__main__":

    optionsURL = "https://finance.yahoo.com/quote/SPY/options/?straddle=false"
    stockURL = "https://finance.yahoo.com/quote/SPY/"
    scrape(optionsURL,stockURL)









