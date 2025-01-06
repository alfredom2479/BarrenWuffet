import requests
import discord
from discord.ext import commands,tasks
import datetime
import pytz
from dotenv import load_dotenv
import os

load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

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



intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    daily_update.start()

@bot.command(name='skibidi')
async def skibidi(ctx):
    await ctx.send('skibidi toilet ')

@bot.command(name='trending')
async def trending(ctx):
    trending_tickers = get_trending_tickers()
    trending_msg = "Trending Tickers:\n"
    for ticker in trending_tickers:
        trending_msg += f"{ticker['name']} ({ticker['symbol']}): ${ticker['previous_close']} -> ${ticker['price']} = ${ticker['price_change']} ({ticker['percent_change']}%)\n"
    await ctx.send(trending_msg[:1995])

@bot.command(name='movers')
async def movers(ctx):
    movers = get_market_movers()
    movers_msg = "Market Movers:\n"
    for category, stocks in movers.items():
        movers_msg += f"{category}:\n"
        for stock in stocks:
            movers_msg += f"  {stock['symbol']}: ${stock['price']} on {stock['exchange']}\n"
    await ctx.send(movers_msg[:1995])


@bot.command(name='analyze')
async def analyze(ctx,*, ticker_id):
    analysis = get_analysis(ticker_id.strip().lower())
    if analysis is None:
        await ctx.send("No analysis found for this ticker")
    else:
        for i,article in enumerate(analysis,1):
            publish_date = datetime.datetime.fromisoformat(article['date_published'])
            if publish_date < datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=730):
                break
            analysis_msg = f"{i}. {article['title']}\n"
            analysis_msg += f"  {article['date_published']}\n"
            if article['structuredInsights']:
                analysis_msg += f"  {article['structuredInsights']}\n"
            await ctx.send(analysis_msg[:1995])


@tasks.loop(time=datetime.time(hour=4,tzinfo=pytz.timezone('US/Eastern')) )
async def daily_update():
    eastern = pytz.timezone('US/Eastern')
    current_time = datetime.datetime.now(eastern)
    print(f"Daily Update Started at {current_time}")

    channel = bot.get_channel(1325527341077758003)

    gainers, gainers_news = get_real_time_gainers()
    losers, losers_news = get_real_time_losers()

    gainers_msg = "Top Gainers:\n"
    for i,gainer in enumerate(gainers,1):
        if (gainer['change_percent'] < 10) or (gainer['price'] > 100 and gainer['change_percent'] < 20):
            continue
        gainers_msg += f"{i}. {gainer['name']} ({gainer['symbol']}) : {gainer['previous_close']} -> {gainer['price']} = {gainer['change']} ({gainer['change_percent']}%)\n"
        gainers_msg += f"  Last Updated: {gainer['last_updated']}\n"

    losers_msg = "Top Losers:\n"
    for i,loser in enumerate(losers,1):
        if (loser['change_percent'] > -10) or (loser['price'] > 100 and loser['change_percent'] > -20):
            continue
        losers_msg += f"{i}. {loser['name']} ({loser['symbol']}) : {loser['previous_close']} -> {loser['price']} = {loser['change']} ({loser['change_percent']}%)\n"
        losers_msg += f"  Last Updated: {loser['last_updated']}\n"


    await channel.send(gainers_msg[:1995])
    await channel.send(losers_msg[:1995])

    channel = bot.get_channel(1325519437687820319)

    
    gainers_news_msg = "Gainers News:\n"
    for news in gainers_news:
        gainers_news_msg += f"{news['title']}\n"
        gainers_news_msg += f"  {news['published_at']}\n"
        if len(news['stocks']) > 0:
            gainers_news_msg += f"  Stocks: {', '.join([stock['symbol'] for stock in news['stocks'] if 'symbol' in stock])}\n"
        else:
            gainers_news_msg += "  Stocks: None\n"
    await channel.send(gainers_news_msg[:1995])

    losers_news_msg = "Losers News:\n"
    for news in losers_news:
        losers_news_msg += f"{news['title']}\n"
        losers_news_msg += f"  {news['published_at']}\n"
        if len(news['stocks']) > 0:
            losers_news_msg += f"  Stocks: {', '.join([stock['symbol'] for stock in news['stocks'] if 'symbol' in stock])}\n"
        else:
            losers_news_msg += "  Stocks: None\n"
    await channel.send(losers_news_msg[:1995])


    yahoo_news = get_news()
    seeking_alpha_news = get_sa_articles()

    news_msg = "Yahoo News:\n"
    for i,article in enumerate(yahoo_news,1):
        if not article['relevant_tickers']:
            continue
        news_msg += f"{i}. {article['title']} ({article['provider']})\n"
        news_msg += f"  {article['date_published']}\n"
        news_msg += f"  {article['preview_url']}\n"
        
        news_msg += f"  Relevant Tickers: {', '.join([ticker['symbol'] for ticker in article['relevant_tickers']])} \n"

    await channel.send(news_msg[:1995])

    sa_news_msg = "Seeking Alpha News:\n"
    for i,article in enumerate(seeking_alpha_news,1):
        sa_news_msg += f"{i}. {article['title']}\n"
        sa_news_msg += f"  {article['date_published']}\n"
        if article['structuredInsights']:
            sa_news_msg += f"  {article['structuredInsights']}\n"
        await channel.send(sa_news_msg[:1995])
        sa_news_msg = ""

    print("Daily Update Completed")

@daily_update.before_loop
async def before_daily_update():
    print("Waiting for bot to be ready...")
    await bot.wait_until_ready()
    print("Bot is ready")


bot.run(DISCORD_TOKEN)

