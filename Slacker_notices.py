# Slacker_notices.py

from Slacker_notice_functions import *
from datetime import datetime
import urllib.request

Token = 'xoxb-6408447014594-6407348963125-DfMu5C1bWtMQjeSNeB1Ak3AF' # 자신의 Token 입력
image_url, trend, today_value = KospiRead()
today_date = datetime.today().strftime('%Y-%m-%d')
image_name = 'E:/Python/slack_notice/images/' + today_date + '_KOSPI.png' # 파일 경로, 이름 지정 : 날짜_KOSPI.png
urllib.request.urlretrieve(image_url, image_name) # 해당 경로에 이미지 저장
upload_image = (image_name, open(image_name, 'rb'), 'png') # 이미지 형식 지정. 경로, 바이트 타입 파일 파싱, 파일 타입

weekdays_dict = {
    0 : '월',
    1 : '화',
    2 : '수',
    3 : '목',
    4 : '금',
    5 : '토',
    6 : '일'
}

weekdays = datetime.weekday(datetime.today())

if weekdays == 5 or weekdays == 6:
    print(f'weekdays : {weekdays}')
else:
    str1_title = 'KOSPI, ' + today_date + ' (' + weekdays_dict[weekdays] + ')'

    buySell = '개인 : ' + trend[0] + ', 외국인 : ' + trend[1] + ', 기관 : ' + trend[2] + '\n'
    programBuySell = '차익 : ' + trend[3] + ', 비차익 : ' + trend[4] + ', 총합 : ' + trend[5] + '\n'
    kospi_value = today_value[0] + today_value[1] + '\n'
    total_text = kospi_value + buySell + programBuySell

    if today_value[1].find('+') != -1: # + 인 경우,
        today_color = '#ff0000' # 빨강색
    else:
        today_color = '#0000ff' # 파랑색


    attach_dict = {
        'color' : today_color,
        'author_name' : '오늘의 증시 알림',
        'title' : str1_title,
        'title_link' : 'http://finance.naver.com/sise/sise_index.nhn?code=KOSPI',
        'text' : total_text
    }
    
    attach_list=[attach_dict]
    
    notice_message(Token, "#stock_notice", str1_title, attach_list)
    upload_file(Token, "#stock_notice", upload_image, today_date + '_KOSPI.png')
    