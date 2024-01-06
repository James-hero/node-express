import pyupbit
import time
import datetime
import requests
import numpy as np
import lxml

myToken = "xoxb-6408447014594-6410905852068-JOuFqZq1wXLbKMOtplvaX6Y3"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_rsi(df, period=14):

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

    return rsi

tickers = pyupbit.get_tickers("KRW")	# KRW를 통해 거래되는 코인만 불러오기
dic_ticker = {}


while True:
    try:

        for target_ticker in tickers:
            df_min60 = pyupbit.get_ohlcv(target_ticker, interval="minute60")     # 일봉 정보
            rsi14 = get_rsi(df_min60, 14).iloc[-1]                          # 당일 RSI
            # before_rsi14 = get_rsi(df_min60, 14).iloc[-2]                   # 작일 RSI
            df_min60['name'] = target_ticker
                        
        
            if df_min60.iloc[-1]['rsi'] < 30:
                # print(df_min60.iloc[-1]['rsi'])
                attach_list = 'NAME : ' + df_min60.iloc[-1]['name'] + '\n'  + 'RSI : ' + str(f'{rsi14:.2f}') + '\n' + '가격 : ' + str(df_min60.iloc[-1]['close'])
                # f'{n:.3f}'
                # print("{:.2f}".format(3.55555))
                # print(df_min60.iloc[-1])
                post_message(myToken,"#crypto", attach_list)
        time.sleep(1)

    except Exception as e:
        print(e)
        post_message(myToken,"#crypto", e)
        time.sleep(1)
