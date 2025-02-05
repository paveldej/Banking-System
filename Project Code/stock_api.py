import requests
#J8OEZ7A6X2DA73UR
#CHG0S2E7GRX9FADV
# THIS TWO ARE KEYS FOR THE API


#THIS FUNCTION RETURNS THE ORIGINAL NAME OF THE API
#THIS IS THE MANE YOU SHHOULD STORE IT AS WHEN HE PURCHASES IT
def get_name(name): 
    try:
        url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={name}&apikey=CHG0S2E7GRX9FADV'
        r = requests.get(url)
        data = r.json()
     #   print(data)
        if "bestMatches" in data.keys():
            return data["bestMatches"][0]["1. symbol"]
        else:
            return None
    except:
        return None

#CHECKS IF THE STOCK NAME IS IN THE API
def find_name(name): 
    try:
        url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={name}&apikey=CHG0S2E7GRX9FADV'
        r = requests.get(url)
        data = r.json()

        if "bestMatches" in data.keys():
            return True
        else:
            return None
    except:
        return None



#RETURNS THE PRICE OF THE STOCK
def get_price(name):
    try:
        name = get_name(name)
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={name}&apikey=CHG0S2E7GRX9FADV'
        r = requests.get(url)
        data = r.json()
        if "Time Series (Daily)" in data.keys():
            price_daily = data["Time Series (Daily)"]
            sorted(price_daily)
            reversed(price_daily)
            first_key = list(price_daily.keys())[0]
            return float(price_daily[first_key]["4. close"])* 10

        else:
            return None
    except:
        return None
