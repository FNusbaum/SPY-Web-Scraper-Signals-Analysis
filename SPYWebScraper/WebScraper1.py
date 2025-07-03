import ssl
import certifi
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import gzip
from io import BytesIO
from bs4 import BeautifulSoup
import time
import csv


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

#returns dictionary with all options info -- keys are strike prices, elements are arrays:
# [lastPrice, bidCall, askCall, change, %change, impliedVolatility, STRIKE, lastPrice, bidPut, askPut, change, %change, impliedVolatility,]
def extract_options_prices(html):
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
                    newDict[strike_price] = [cells[3].text, cells[4].text, cells[5].text, cells[6].text, cells[7].text, cells[10].text, strike_price]
       
        #array = newDict.keys()
        put_table = putTable[0]
        if put_table:
            putRows = put_table.find_all('tr')
            for row in putRows[1:]:
                cells = row.find_all('td')
                strike_price = float(cells[2].text.replace(',', ''))
                if abs(strike_price - current_price) <= current_price*0.02:
                    if strike_price in newDict:
                        newDict[strike_price] += [cells[3].text, cells[4].text, cells[5].text, cells[6].text, cells[7].text, cells[10].text]
       #                 array.remove(key)
                    else:
                        newDict[strike_price] = ['-','-','-','-','-','-', strike_price, cells[3].text, cells[4].text, cells[5].text, cells[6].text, cells[7].text, cells[10].text]
       # for i in range(len(list)):
       #     newDict[list[i]] += ['-','-','-','-','-','-']
        return newDict



if __name__ == "__main__":

    currentTime = time.time()
    local_time = time.localtime(currentTime)
    time_of_day = time.strftime("%H:%M:%S", local_time)  #current time
    hour = int(time_of_day[0:2])

    url = "https://finance.yahoo.com/quote/SPY/options/?straddle=false"
    stockDayTable = [['TimeOfDay', 'Price']]

    #while hour < 16:
    count = 0
    while count < 1:
        array = []
        html_content = fetch_html(url)

        currentTime = time.time()
        local_time = time.localtime(currentTime)
        time_of_day = time.strftime("%H:%M:%S", local_time)

        if html_content:
            stock_price = extract_stock_price(html_content)
            if stock_price:
                array = [[time_of_day, stock_price]]
            else:
                array = [[time_of_day, ]]
        else:
            array = [[time_of_day, ]]
        stockDayTable += array
        time.sleep(1)  # Wait for X seconds before fetching the data again

        count +=1

    
           # dictionary = extract_options_prices(html_content)




