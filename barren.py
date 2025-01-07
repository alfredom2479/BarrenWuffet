import discord
from discord.ext import commands,tasks
import csv
import datetime
import pytz
from dotenv import load_dotenv
import os
from api_funcs import (
    get_trending_tickers, 
    get_market_movers, 
    get_real_time_gainers, 
    get_real_time_losers, 
    get_news, 
    get_sa_articles, 
    get_analysis
)

load_dotenv()
# RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


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


@bot.command(name='add')
async def add(ctx, ticker_id=None, avg_cost=None, quantity=None):
    # Check if all parameters are provided
    print(ticker_id, avg_cost, quantity)
    if ticker_id is None or avg_cost is None or quantity is None:
        await ctx.send("Please provide all required parameters: ticker_id, avg_cost, and quantity")
        return

    # Validate and convert values
    try:
        ticker_id = ticker_id.strip().upper()
        if not ticker_id:
            await ctx.send("Ticker ID cannot be empty")
            return
            
        avg_cost = float(avg_cost)
        if avg_cost <= 0:
            await ctx.send("Average cost must be greater than 0")
            return

        quantity = int(quantity)
        if quantity <= 0:
            await ctx.send("Quantity must be greater than 0")
            return

    except ValueError:
        await ctx.send("Invalid values provided. Please check the format and try again")
        return

    # Add to CSV file
    try:
        with open('portfolio.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ticker_id, avg_cost, quantity])
        await ctx.send(f"Successfully added {quantity} shares of {ticker_id} at ${avg_cost:.2f} per share")
    except IOError:
        await ctx.send("Error writing to portfolio file")
        return

@bot.command(name='mod')
async def mod(ctx, ticker_id=None, mod_type=None, value=None):
    # Check if all parameters are provided
    if ticker_id is None or mod_type is None or value is None:
        await ctx.send("Please provide all required parameters: ticker_id mod_type value")
        return

    # Validate inputs
    ticker_id = ticker_id.strip().upper()
    mod_type = mod_type.lower()
    
    # Verify mod_type is valid
    if mod_type not in ['cost', 'quant']:
        await ctx.send("mod_type must be either 'cost' or 'quant'")
        return

    # Validate and convert value
    try:
        value = float(value) if mod_type == 'cost' else int(value)
        if value <= 0:
            await ctx.send(f"Value must be greater than 0")
            return
    except ValueError:
        await ctx.send(f"Invalid value provided. Please provide a {'number' if mod_type == 'cost' else 'whole number'}")
        return

    # Read and modify the CSV file
    found = False
    updated_rows = []
    try:
        with open('portfolio.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == ticker_id:
                    found = True
                    # Modify either cost (index 1) or quantity (index 2)
                    row[1 if mod_type == 'cost' else 2] = value
                updated_rows.append(row)

        if not found:
            await ctx.send(f"Ticker {ticker_id} not found in portfolio")
            return

        # Write back to CSV
        with open('portfolio.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

        await ctx.send(f"Successfully updated {ticker_id}'s {mod_type} to {value}")

    except IOError:
        await ctx.send("Error accessing portfolio file")
        return

@bot.command(name='remove')
async def remove(ctx, ticker_id=None):
    # Check if ticker_id is provided
    if ticker_id is None:
        await ctx.send("Please provide a ticker_id to delete")
        return

    ticker_id = ticker_id.strip().upper()
    found = False
    updated_rows = []

    try:
        # Read the CSV and filter out the matching ticker
        with open('portfolio.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == ticker_id:
                    found = True
                else:
                    updated_rows.append(row)

        if not found:
            await ctx.send(f"Ticker {ticker_id} not found in portfolio")
            return

        # Write back the filtered rows
        with open('portfolio.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

        await ctx.send(f"Successfully deleted {ticker_id} from portfolio")

    except IOError:
        await ctx.send("Error accessing portfolio file")
        return

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

