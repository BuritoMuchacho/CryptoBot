import config  # config.py file with token
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from sqliter import SQLiter  # class to work with database
import yfinance as yf  # Yahoo! Finance API


logging.basicConfig(level=logging.INFO)  # set logging level
bot = Bot(token=config.TOKEN)  # initialize bot
dp = Dispatcher(bot)
db = SQLiter('db.db')  # use class with our database


def get_price(ticker, partition, point=None):
    """Get formated prices"""
    ticker_yahoo = yf.Ticker(ticker)
    data = ticker_yahoo.history()  # get price history
    if partition == True:
        last_quote = str(data.tail(1)['Close'].iloc[0]).partition('.')[
            0]  # get last price
    else:
        last_quote = str(data.tail(1)['Close'].iloc[0])[:point]
    link = 'https://finance.yahoo.com/quote/' + ticker
    return ticker[:-4], last_quote, link


async def send_prices(wait_for):
    """Send prices to user"""
    old_prices = []  # list of prices an hour ago
    while True:
        prices = []  # prices list
        tickers = ['BTC-USD', 'ETH-USD', 'BNB-USD']  # currencies

        for ticker in tickers:
            ticker, last_quote, link = get_price(ticker, partition=True)
            prices.append(f'{ticker}: {last_quote}$\n{link}\n')

        message = ''  # message to user
        if old_prices:  # compare prices
            if prices[0] > old_prices[0]:
                message += '📈' + prices[0] + '\n'
            elif prices[0] == old_prices[0]:
                message += prices[0] + '\n'
            else:
                message += '📉' + prices[0] + '\n'
            if prices[1] > old_prices[1]:
                message += '📈' + prices[1] + '\n'
            elif prices[1] == old_prices[1]:
                message += prices[1] + '\n'
            else:
                message += '📉' + prices[1] + '\n'
            if prices[2] > old_prices[2]:
                message += '📈' + prices[2] + '\n'
            elif prices[2] == old_prices[2]:
                message += prices[2] + '\n'
            else:
                message += '📉' + prices[2] + '\n'
        else:
            message += prices[0] + '\n'
            message += prices[1] + '\n'
            message += prices[2] + '\n'

        old_prices = prices  # prices to be compared later

        subscriptions = db.get_subscriptions()  # get subscriprions from database
        for s in subscriptions:
            await bot.send_message(s[1], message)  # send prices to user
        await asyncio.sleep(wait_for)  # wait


@dp.message_handler(commands=['sub'])
async def sub(message: types.Message):
    """Subscribe user"""
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user.id)  # add subscribed user
    else:
        db.upgrade_subscrption(message.from_user.id, True)  # subscribe user

    await message.answer("You have succesfully subscribed!")


@dp.message_handler(commands=['unsub'])
async def unsub(message: types.Message):
    """Unsubscribe user"""
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user.id, False)  # add unsubscribed user
        await message.answer("You aren't subscribed")
    else:
        db.upgrade_subscrption(message.from_user.id, False)  # unsubscribe user
        await message.answer("You have succesfully unsubscribed.")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """Start message"""
    await message.answer("Hey! This bot can send you prices of cryptocurrencies every hour. It uses Yahoo! Finance API. Type /help to get more information!")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    """Help message"""
    await message.answer("To subscribe and recieve prices of Bitcoin, Ethereum and BinanceCoin type /sub. \nIf you don't want to recieve those prices anymore type /unsub. \nTo get supported currencies list type /list.")


@dp.message_handler(commands=['list'])
async def list(message: types.Message):
    """Help message"""
    await message.answer("/btc - Bitcoin\n/eth - Ethereum\n/bnb - BinanceCoin\n/ada - Cardano\n/doge - Dogecoin\n/ltc - Litecoin\n/bch - BitcoinCash\n/xmr - Monero")


@dp.message_handler(commands=['btc'])
async def btc(message: types.Message):
    ticker, last_quote, link = get_price('BTC-USD', partition=True)
    await message.answer(f'{ticker}: {last_quote}$\n\n{link}')


@dp.message_handler(commands=['eth'])
async def eth(message: types.Message):
    ticker, last_quote, link = get_price('ETH-USD', partition=True)
    await message.answer(f'{ticker}: {last_quote}$\n\n{link}')


@dp.message_handler(commands=['bnb'])
async def bnb(message: types.Message):
    ticker, last_quote, link = get_price('BNB-USD', partition=False, point=5)
    await message.answer(f'{ticker}: {last_quote}$\n\n{link}')


@dp.message_handler(commands=['ada'])
async def ada(message: types.Message):
    ticker, last_quote, link = get_price('ADA-USD', partition=False, point=5)
    await message.answer(f'{ticker}: {last_quote}$\n\n{link}')


@dp.message_handler(commands=['doge'])
async def doge(message: types.Message):
    ticker, last_quote, link = get_price('DOGE-USD', partition=False, point=5)
    await message.answer(f'{ticker}: {last_quote}$\n\n{link}')


@dp.message_handler(commands=['bch'])
async def bch(message: types.Message):
    ticker, last_quote, link = get_price('BCH-USD', partition=False, point=5)
    await message.answer(f'{ticker}: {last_quote}$\n\n{link}')


@dp.message_handler(commands=['ltc'])
async def ltc(message: types.Message):
    ticker, last_quote, link = get_price('LTC-USD', partition=False, point=5)
    await message.answer(f'{ticker}: {last_quote}$\n\n{link}')


@dp.message_handler(commands=['xmr'])
async def xmr(message: types.Message):
    ticker, last_quote, link = get_price('XMR-USD', partition=False, point=5)
    await message.answer(f'{ticker}: {last_quote}$\n\n{link}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # send prices every 3600 seconds (an hour)
    loop.create_task(send_prices(3600))
    executor.start_polling(dp, skip_updates=True)  # start the bot
