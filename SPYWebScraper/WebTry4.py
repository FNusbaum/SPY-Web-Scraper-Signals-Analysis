import ssl
import certifi
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import gzip
from io import BytesIO
from bs4 import BeautifulSoup
import time


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

#calls just below and above strike, expiring today
def extract_options_prices(html):
    soup = BeautifulSoup(html, 'html.parser')
    current_price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    if current_price_tag:
        current_price = float(current_price_tag.text.replace(',', ''))
        options_table = soup.find('table', class_='svelte-hto7i0')
        if options_table:
            rows = options_table.find_all('tr')
            for row in rows[1:]:  # Skipping header row
                cells = row.find_all('td')
                strike_price = float(cells[5].text.replace(',', ''))

                last_call_price = cells[0].text
                last_put_price = cells[6].text
                #call_bid_price = cells[4].text
                #call_ask_price = cells[5].text  
                #put_bid_price  = 
                #ptu_ask_price =               
                if abs(strike_price - current_price) <= current_price*0.02:
                    #print(f"Call Option (Strike Price: {strike_price}, Bid: {bid_price}, Ask: {ask_price})")
                    print(f"Strike={strike_price}: last call = {last_call_price}, last put = {last_put_price}")


#comment this or the other one out for obvious reasons.
'''def extract_options_prices(html):
    soup = BeautifulSoup(html, 'html.parser')
    current_price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    if current_price_tag:
        current_price = float(current_price_tag.text.replace(',', ''))
        options_table = soup.find('table', class_='svelte-hto7i0')
        if options_table:
            rows = options_table.find_all('tr')
            for row in rows[1:]:  # Skipping header row
                cells = row.find_all('td')
                strike_price = float(cells[7].text.replace(',', ''))
                call_bid_price = cells[1].text
                call_ask_price = cells[2].text  
                put_bid_price  = cells[9].text  
                put_ask_price = cells[10].text                
                if abs(strike_price - current_price) <= current_price*0.02:
                    print(f"Strike={strike_price}: callSpread = {call_bid_price} @ {call_ask_price}, putSpread = {put_bid_price} @ {put_ask_price}")
'''


if __name__ == "__main__":
    url = "https://finance.yahoo.com/quote/SPY/options/?straddle=true"
    count = 0
    while count< 3:
        html_content = fetch_html(url)
        if html_content:
            stock_price = extract_stock_price(html_content)
            if stock_price:
                print(f"Stock Price: {stock_price};  Time: {time.time()}")
            else:
                print("Could not find the stock price.")
            extract_options_prices(html_content)
            print("")
        count +=1
        time.sleep(0)  # Wait for X seconds before fetching the data again


