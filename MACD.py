import math
import linchackathon as lh
import pandas as pd

lh.init('f4c80833-9a27-4f76-8cbc-0c088df064cc')

tickers = lh.getTickers()
tickers.remove('BOND1')
tickers.remove('BOND2')
longema = 24
shortema = 12
signalema = 9

#Calculates simple moving average, currently not used
def sma(data: list):
    sum(data)/len(data)

#Calculates expontial moving average
def ema(data: pd.DataFrame, days: int):
   return data.ewm(span=days, adjust=False).mean()
    
#Calculates mean for a specific stock using its dataframe
def stockMean(stockHistory: pd.DataFrame):
    openHighLowClose = stockHistory[['askOpen', 'bidOpen', 'askClose', 'bidClose', 'askHigh', 'bidHigh', 'askLow', 'bidLow']]
    openHighLowClose['mean'] = openHighLowClose.mean(axis=1)
    mean = openHighLowClose['mean']
    return mean


#macd algorithm, returns buyin signal 1, selling signal -1
def macd(ticker: str ,shortEMATime : int, longEMATime: int, signalEMATime: int):

    history = pd.DataFrame(lh.getStockHistory(ticker, 3))

    mean = stockMean(history)

    emaShort = ema(mean, shortEMATime)
    emaLong = ema(mean, longEMATime)
    emaSignal = ema(mean, signalEMATime)
    
    if (len(emaLong) < longEMATime):
        print("length under longema")
        return 0
    macdSignalratio = (emaSignal[emaSignal.last_valid_index()]+ emaShort[emaShort.last_valid_index()]-emaLong[emaLong.last_valid_index()])/emaSignal[emaSignal.last_valid_index()]
    print(macdSignalratio)
    if macdSignalratio > 1:
        print("buyingtime")
        return 1
    elif macdSignalratio < 1:
        print("sellingtime")
        return -1
    else:
        print("do nothing")
        return 0

#Executes the buying an selling
def excecute(ticker: str, signal: int):
    portfolio = pd.DataFrame(lh.getPortfolio())
    if ticker in portfolio:
            position = portfolio[ticker]
    else :
        return 'nothing'

    if position > 0 and signal == -1:
        lh.sellStock(ticker, position)
        return 'sold'
    elif signal == 1:
        return ticker
    else:
        return 'nothing'

#sells all of holdings in stock
def sellAll(ticker: str):
    lh.sellStock(ticker, lh.getPortfolio[ticker])

#sells amount in cash of stock
def sellStock(ticker: str, amount: int):
    sellAmount = math.trunc(amount/lh.getStock(ticker)['bidClose'])
    lh.sellStock(ticker, sellAmount)

#buy all we can of specific stock
def buyAll(ticker: str):
    canAfford = math.trunc(lh.getSaldo()/lh.getStock(ticker)['askClose'])
    lh.buyStock(ticker, canAfford)

#get networth
def getNetworth():
    cash = lh.getSaldo()
    portfolio = lh.getPortfolio
    for ticker in portfolio:
        cash += getHoldValue(ticker)
    return cash

#get value of holdings in specific stock
def getHoldValue(ticker: str):
    tickerCurrentPrize = lh.getStock(ticker)
    portfolio = lh.getPortfolio
    position = portfolio[ticker]
    return tickerCurrentPrize*position
        

#spreads our holdings
def equalize(filteredStocklist: list):
    moneyPerStock = getNetworth()/len(filteredStocklist)
    filteredStocklist(key=lambda x: getHoldValue(x), reverse=True)
    for stock in filteredStocklist:
        diff = getHoldValue(stock) - moneyPerStock
        excessiveAmount = (diff / lh.getStock(stock))
        percentageOfNetWorthInStock = getHoldValue(stock)/getNetworth()

        if excessiveAmount > 0 and replace(filteredStocklist, percentageOfNetWorthInStock):
            sellStock(stock, getHoldValue(stock)*0.25)
        elif excessiveAmount < 0:
            buyStock(stock, abs(excessiveAmount))
    
#used in equalize to determine wheter we should spread or not
def replace(stockList: list, percentageOfNetWorthInStock):

    if len(stockList) >  3 and percentageOfNetWorthInStock > 0.4:
        return True
    else:
        return False
        

#buys amount in cash of stock
def buyStock(stock: str, amount: int):
    canAfford = math.trunc(amount/lh.getStock()['askClose'])
    lh.buyStock(stock, canAfford)

#buys stock
def buyAlgorithm(filteredBullList: list):
    standardBuy = 0.25
    if len(filteredBullList) > 1/standardBuy:
        standardBuy = 1/len(filteredBullList)
    for ticker in filteredBullList:
        percentageOfNetWorthInStock = getHoldValue(ticker)/getNetworth()
        if percentageOfNetWorthInStock < 0.15:
            buyStock(ticker, standardBuy - percentageOfNetWorthInStock)


def condition():
    return False

#main function
def main ():
    while True:
        bull = []
        for ticker in tickers:
            signal = macd(ticker, shortema, longema, signalema)
            bull.append(excecute(ticker, signal))

        filteredBullList = list(filter(lambda a: a != 'sold' and a != 'nothing', bull))
        buyAlgorithm(filteredBullList)

main()
