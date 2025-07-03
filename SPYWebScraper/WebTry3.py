import ssl
import certifi
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import gzip
from io import BytesIO
from bs4 import BeautifulSoup

def fetch_html(url):
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        request = Request(url, headers={'Accept-Encoding': 'gzip'})
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
    # Inspect the Yahoo Finance page to find the correct CSS selector for the stock price
    price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    if price_tag:
        return price_tag.text
    return None

if __name__ == "__main__":
    url = "https://finance.yahoo.com/quote/%5EGSPC/"
    #url = "https://www.google.com/finance/quote/.INX:INDEXSP?hl=en"
    html_content = fetch_html(url)
    if html_content:
        stock_price = extract_stock_price(html_content)
        if stock_price:
            print(f"The stock price is: {stock_price}")
        else:
            print("Could not find the stock price.")
