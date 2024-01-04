import time
import pyupbit
import datetime
import requests
import numpy as np

access = "vWf2xAm3o7yR7IBtZcx2MI59Xy5P2kuJwhPaNh7U"
secret = "johIn3NbSyKEfgxLDdepDxsTupqdKI793D3m8FmF"
myToken = "xoxb-6408447014594-6410905852068-mlHWwHQeyUuDMjTC50ckYCQU"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute30")#, count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    df.to_excel("aa.xlsx")
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    # df.to_excel("bb.xlsx")
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute30")#, count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    df['ma15'] = df['close'].rolling(15).mean().iloc[-1]
    df.to_excel("cc.xlsx")
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_rsi(ticker, period=14):

    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    # df = pyupbit.get_ohlcv(ticker, interval="minute240")

    # 전일 대비 변동 평균
    df['change'] = df['close'].diff()

    # 상승한 가격과 하락한 가격
    df['up'] = df['change'].apply(lambda x: x if x > 0 else 0)
    df['down'] = df['change'].apply(lambda x: -x if x < 0 else 0)

    # 상승 평균과 하락 평균
    df['avg_up'] = df['up'].ewm(alpha=1/period).mean()
    df['avg_down'] = df['down'].ewm(alpha=1/period).mean()

    # 상대강도지수(RSI) 계산
    df['rs'] = df['avg_up'] / df['avg_down']
    df['rsi'] = 100 - (100 / (1 + df['rs']))
    rsi = df['rsi']

    #엑셀로 출력
    df.to_excel("dd.xlsx")

    return rsi

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#crypto", "autotrade start")

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        # btc_day = pyupbit.get_ohlcv(ticker, interval="day")     # 비트코인의 일봉 정보

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            print("ing...")
            yesterday_rsi = get_rsi("KRW-BTC", 14).iloc[-1]   # 하루 전의 RSI14 값을 이용
            # today_rsi = get_rsi(btc_day, 14).iloc[-1] 	# 당일의 RSI14 값을 이용
            if target_price < current_price and ma15 < current_price and yesterday_rsi < 30:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    post_message(myToken,"#crypto", "BTC buy : " +str(buy_result))
            elif yesterday_rsi > 70:
                post_message(myToken,"#crypto", "RSI 70이상")
                btc = get_balance("BTC")
                if btc > 0.00008:
                    sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                    post_message(myToken,"#crypto", "BTC buy : " +str(sell_result))
            elif yesterday_rsi < 30:
                post_message(myToken,"#crypto", "RSI 30미만")
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                post_message(myToken,"#crypto", "BTC buy : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#crypto", e)
        time.sleep(1)