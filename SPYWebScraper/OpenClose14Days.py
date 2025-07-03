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
    file_path = today +'/'+fileName
    with open(file_path, 'a') as file:
        writer = csv.writer(file, dialect = 'excel')
        writer.writerow(row)
        file.close()

def read(fileName, row):
    file_path = today +'/'+fileName
    with open(file_path, 'r') as file:
        reader = csv.reader(file, dialect = 'excel')
        writer.writerow(row)
        file.close()

def highLow_openClose():
	RSIurl = "https://finance.yahoo.com/quote/SPY/history/"
	#table = ['open', 'close'] 14x2
	RSI_content = fetch_html(RSIurl)
	soup = BeautifulSoup(RSI_content, 'html.parser')
	return soup

#Stochastic Oscilator, ranges from 0 to 1, measures overbought/oversold as +80 or -20
#meant to be a longer term indicator, using only closing prices, not current market price.
def stochastic_short_term(soup):
	price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
	if price_tag:
		price  = float(price_tag.text.replace(',',''))
	highs = []
	lows = []
	tableContainer = soup.find('table', class_='table svelte-ewueuo')
	table = tableContainer.find('tbody')
	rows = table.find_all('tr')
	for i in range(14):
		#2 = high, 3 = low
		cells = rows[i].find_all('td')
		highPrice = float(cells[2].text)
		lowPrice = float(cells[3].text)
		highs += [highPrice]
		lows += [lowPrice]
	maxHigh = max(highs)
	minLow = min(lows)
	answer = (price-minLow)/(maxHigh-minLow)
	return answer


#makes table for rsi data from url with open close data
def RSI(soup):

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

if __name__ == "__main__":
	#table = RSItable()
	#gainLossList = gain_loss_sum(table)
	#print(gainLossList)
	#RSI = 100 - 100/(1+((totalGain + currentgain)/(totalLoss + currentloss)))
	soup = highLow_openClose()
	print(RSI(soup))















