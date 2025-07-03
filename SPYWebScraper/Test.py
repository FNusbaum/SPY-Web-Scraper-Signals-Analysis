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
    if count > 9:
        start = count-9
        num=11
        average=0
        nums = []
        for i in range(10):
            try:
                if type(float(stockDayTable[start+i][1])) is float:
                    average += float(stockDayTable[start+i][1])
            except ValueError as e:
                num -= 1
        average += price
        average = average/num
        variance = 0
        for i in range(10):
            try:
                if type(float(stockDayTable[start+i][1])) is float:
                    variance += (float(stockDayTable[start+i][1]) -average)**2
            except ValueError as e:
                continue
        variance += (price -average)**2
        variance = variance/num
        sd = variance**(1/2)

        highBoll = average + 2*sd
        lowBoll = average-2*sd
        Boll = 0
        if float(price) > highBoll:
            Boll = 1
        if float(price) < lowBoll:
            Boll = -1
    info = [time_of_day, float(price), average, Boll, vol]
    return info


if __name__ == "__main__":
	count =0
	url = 'https://finance.yahoo.com/quote/NVDA/'
	html = fetch_html(url)
	table = [['time_of_day', 'price', 'average', 'Boll', 'vol']]
	for i in range(13):
		table += [extract_stock_info(html, count, table)]
		count +=1
		time.sleep(20)
	print(table)









