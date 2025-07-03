from urllib.request import urlopen
from urllib.error import URLError, HTTPError

def fetch_html(url):
    try:
        with urlopen(url) as response:
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


if __name__ == "__main__":
    url = "https://finance.yahoo.com/quote/%5EGSPC/"
    html_content = fetch_html(url)
    if html_content:
        print(html_content)
