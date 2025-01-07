import requests
from dotenv import load_dotenv
import os

load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

def get_market_movers():
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-movers"
    
    querystring = {
        "region": "US",
        "lang": "en-US", 
        "start": "0",
        "count": "6"
    }

    headers = {
        "Accept": "application/json",
        "x-rapidapi-ua": "RapidAPI-Playground",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    results = data['finance']['result']
    market_movers = {}

    for category in results:
        category_name = category['canonicalName']  # e.g., 'DAY_GAINERS'
        stocks = []
        
        for quote in category['quotes']:
            stocks.append({
                'symbol': quote['symbol'],
                'price': quote['regularMarketPrice'],
                'exchange': quote['fullExchangeName']
            })
            
        market_movers[category_name] = stocks
    
    return market_movers

def get_trending_tickers():
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-trending-tickers"
    
    querystring = {
        "region": "US",
    }

    headers = {
        "Accept": "application/json",
        "x-rapidapi-ua": "RapidAPI-Playground",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    results = data['finance']['result'][0]['quotes']
    trending_tickers = []
    for quote in results:
        if 'longName' not in quote:
            continue
        trending_tickers.append({
            'name': quote['longName'] ,
            'symbol': quote['symbol'],
            'price': quote['regularMarketPrice'],
            'exchange': quote['fullExchangeName'],
            'previous_close': quote['regularMarketPreviousClose'],
            'price_change': quote['regularMarketChange'],
            'percent_change': quote['regularMarketChangePercent']
        })

    return trending_tickers

def get_news():
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/v2/list"
    
    querystring = {
        "region": "US",
    }

    headers = {
        "Accept": "application/json",
        "x-rapidapi-ua": "RapidAPI-Playground",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    response = requests.post(url, headers=headers, params=querystring)
    data = response.json()

    #print(data)
    results= data['data']['main']['stream']
    news_articles = []

    for article in results:
        news_articles.append({
            'id': article['content']['id'],
            'title': article['content']['title'],
            'content_type': article['content']['contentType'],
            'date_published': article['content']['pubDate'],
            'preview_url': article['content']['previewUrl'],
            'provider': article['content']['provider']['displayName'],
            'relevant_tickers': article['content']['finance']['stockTickers']
        })

    return news_articles

def get_sa_articles():
    url = "https://seeking-alpha.p.rapidapi.com/articles/v2/list"

    querystring = {
        "category": "latest-articles",
    }

    headers = {
        "Accept": "application/json",
        "x-rapidapi-ua": "RapidAPI-Playground",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "seeking-alpha.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    results = data['data']
    sa_articles = []

    for article in results:
        sa_articles.append({
            'id': article['id'],
            'title': article['attributes']['title'],
            'date_published': article['attributes']['publishOn'],
            'structuredInsights': article['attributes']['structuredInsights'],
        })
    return sa_articles

def get_analysis(id):
    url = "https://seeking-alpha.p.rapidapi.com/analysis/v2/list"

    querystring = {
        "id": id,
    }

    headers = {
        "Accept": "application/json",
        "x-rapidapi-ua": "RapidAPI-Playground",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "seeking-alpha.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    analysis = []

    results = data['data']
    if len(results) == 0:
        return None
    
    for result in results:
        if 'type' not in result or result['type'] != 'article':
            continue
        if 'attributes' not in result or 'structuredInsights' not in result['attributes']:
            continue
        analysis.append({
            'id': result['id'],
            'title': result['attributes']['title'],
            'date_published': result['attributes']['publishOn'],
            'structuredInsights': result['attributes']['structuredInsights'],
        })

    return analysis

def get_real_time_gainers():
    url = "https://real-time-finance-data.p.rapidapi.com/market-trends"

    querystring = {
        "trend_type": "GAINERS",
        "country": "US",
        "language": "en",
    }

    headers = {
        "Accept": "application/json",
        "x-rapidapi-ua": "RapidAPI-Playground",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "real-time-finance-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    results = data['data']['trends']
    news_results = data['data']['news']
    real_time_gainers = []
    gainers_news = []

    for ticker in results:
        real_time_gainers.append({
            'symbol': ticker['symbol'],
            'name': ticker['name'],
            'price': ticker['price'],
            'previous_close': ticker['previous_close'],
            'change': ticker['change'],
            'change_percent': ticker['change_percent'],
            # 'closed_market_price': ticker['pre_or_post_market'],
            'last_updated': ticker['last_update_utc'],
        })
    for news in news_results:
        gainers_news.append({
            'title': news['article_title'],
            'url': news['article_url'],
            'published_at': news['post_time_utc'],
            'stocks': news['stocks_in_news'],
        })

    return real_time_gainers, gainers_news

def get_real_time_losers():
    url = "https://real-time-finance-data.p.rapidapi.com/market-trends"

    querystring = {
        "trend_type": "LOSERS",
        "country": "US",
        "language": "en",
    }

    headers = {
        "Accept": "application/json",
        "x-rapidapi-ua": "RapidAPI-Playground",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "real-time-finance-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    results = data['data']['trends']
    news_results = data['data']['news']
    real_time_losers = []
    losers_news = []

    for ticker in results:
        real_time_losers.append({
            'symbol': ticker['symbol'],
            'name': ticker['name'],
            'price': ticker['price'],
            'previous_close': ticker['previous_close'],
            'change': ticker['change'],
            'change_percent': ticker['change_percent'],
            # 'closed_market_price': ticker['pre_or_post_market'],
            'last_updated': ticker['last_update_utc'],
        })
    for news in news_results:
        losers_news.append({
            'title': news['article_title'],
            'url': news['article_url'],
            'published_at': news['post_time_utc'],
            'stocks': news['stocks_in_news'],
        })

    return real_time_losers, losers_news