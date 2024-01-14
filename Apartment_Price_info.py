# 1-1. 데이터 가져오기
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import dataframe_image as dfi
import schedule
import time
import json
from bs4 import BeautifulSoup
from colorama import Fore, init
import pandas as pd


def get_items(response):
    root = ET.fromstring(response.content)
    item_list = []
    for child in root.find('body').find('items'):
        elements = child.findall('*')
        data = {}
        for element in elements:
            tag = element.tag.strip()
            text = element.text.strip()
            # print tag, text
            data[tag] = text
        item_list.append(data)  
    return item_list

def notice_message(token, channel, text, attachments):
    '''
    메시지를 보내는 부분. 함수 안 argument 순서 : \n
    token : Slack Bot의 토큰
    channel : 메시지를 보낼 채널 #stock_notice
    text : Slack Bot 이 보낼 텍스트 메시지. 마크다운 형식이 지원된다.
    attachments : 링크. 텍스트 이외에 URL 이미지등을 첨부할 수 있다.
    '''
    attachments = json.dumps(attachments) # 리스트는 Json 으로 덤핑 시켜야 Slack한테 제대로 간다.
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel, "text": text ,"attachments": attachments})

def upload_file(token, channel, files, filename):
    '''
    Slack API 직접호출 파일 업로드 함수. 함수 안 argument 순서 : \n
    token : Slack Bot의 토큰
    channel : 메시지를 보낼 채널 #stock_notice
    files : 첨부파일. 로컬 컴퓨터에서 이미지, pdf 문서등을 업로드 할 수 있다.
    '''

    response2 = requests.post("https://slack.com/api/files.upload",
        headers={"Authorization": "Bearer "+token},
        data={"channels": channel, "filename": filename},
        files = {"file": files})

    
def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )    

def notice_text(token, channel, text):
    '''
    Slack Bot 에 텍스트만 전달하는 함수\n
    token : 개인 토큰 코드
    channel : Slack Workspace 채널
    text : 보내고 싶은 메시지
    '''
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel, "text": text})    


weekdays_dict = {
    0 : '월',
    1 : '화',
    2 : '수',
    3 : '목',
    4 : '금',
    5 : '토',
    6 : '일'
}

def job():

    weekdays = datetime.weekday(datetime.today())
    Token = 'xoxb-6408447014594-6407348963125-z8pl9oc2u0kdwIaQDwiCA4WB' # 자신의 Token 입력
    today_date = datetime.today().strftime('%Y-%m-%d')
    

    if weekdays == 5 or weekdays == 6:
        print(f'weekdays : {weekdays}')

    else:

        str1_title = '아파트 매매 실거래가, ' + today_date + ' (' + weekdays_dict[weekdays] + ')'


        image_name = '/home/ubuntu/node-express/Slack_notice/images/estate_' + today_date + '_image.png' # 파일 경로, 이름 지정 : .png
        # urllib.request.urlretrieve(image_url, image_name) # 해당 경로에 이미지 저장
        upload_image = (image_name, open(image_name, 'rb'), 'png') # 이미지 형식 지정. 경로, 바이트 타입 파일 파싱, 파일 타입


        url ="http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?"
        service_key = "f8jvMx8plCiIVNuTpicl8vSQgAuNfuxGya9yk5GUAPeaqrqHS5fake29s6wghpOZvyKyEtoIQCASqtOhmfqjSA%3D%3D"
        base_date = datetime.today().strftime('%Y%m')
        gu_code = '41220' ## 법정동 코드 5자리라면, 구 단위로 데이터를 확보하는 것. 11215 = 광진구

        payload = "LAWD_CD=" + gu_code + "&" + \
                "DEAL_YMD=" + base_date + "&" + \
                "serviceKey=" + service_key + "&" 
                
        res = requests.get(url + payload)
        print(res)


        items_list = get_items(res)
        items = pd.DataFrame(items_list) 
        items['거래일자'] = items['년'] + '-' +  items['월'].astype(str).str.zfill(2) + '-' + items['일'].astype(str).str.zfill(2)
        # 앞에 0을 붙이거나 그대로 출력
        # formatted_date_with_zero = formatted_date[:8] + formatted_date[8:].rjust(2, '0')
        # f"{year}-{month:02d}-{day:02d}"

        # items
        # items.loc[items['거래일자'] = datetime.now()]
        today = items[(items['거래일자']== "2024-01-08")]
            #    datetime.now().strftime("%Y-%m-%d"))]

        # today.to_csv(os.path.join("%s_%s~%s.csv" %(gu, year[0], year[-1])), index=False,encoding="euc-kr") 

        data = today[['거래일자', '년','월','일','아파트', '전용면적', '층', '거래금액', '건축년도', '법정동', '거래유형', '중개사소재지','지역코드']]
        data['일'] = data['일'].astype(int)
        data = data.sort_values(by=['지역코드','일'], ascending= True)

        data = data.reset_index(drop=True)
        data = data.set_index(['거래일자'])

        dfi.export(data, './estate_' + today_date + '_image.png', max_cols = -1, max_rows = -1)
        # image_name = 'E:/Python/cryptoauto/_estate' + today_date + '_image.png' # 파일 경로, 이름 지정 : .png
        data.to_csv('estate_today.csv', index=True, encoding="euc-kr") 



        # attach_dict = {
        #     # 'color' : today_color,
        #     'author_name' : '오늘의 아파트 매매 실거래가 알림',
        #     'title' : str1_title,
        #     'title_link' : '중요 포인트!!!',
        #     'text' : data
        # }
        
        # attach_list=[data]

        # Get the current time
        current_time = datetime.now().time()

        # Extract the hour from the current time
        current_hour = current_time.hour

        # Check if it's morning or afternoon
        if current_hour < 12:
            # Morning
            upload_file(Token, "#stock_notice", upload_image, 'estate_' + today_date + '_image.png')

        else:
            # Afternoon
            for i in range(0, data.shape[0]):
                attach_list = '거래일자 : ' + data.index[i] + ' | '  + '아파트 : ' + data.iloc[i]['아파트'] + ' | ' + '전용면적 : ' + data.iloc[i]['전용면적']  + ' | ' + '층 : ' + data.iloc[i]['층']  + ' | ' + '거래금액 : ' + data.iloc[i]['거래금액']  + ' | ' + '건축년도 : ' + data.iloc[i]['건축년도']  + ' | ' + '법정동 : ' + data.iloc[i]['법정동']  + ' | ' + '거래유형 : ' + data.iloc[i]['거래유형']  + ' | ' + '중개사소재지 : ' + data.iloc[i]['중개사소재지']  + ' | ' + '지역코드 : ' + data.iloc[i]['지역코드'] + ' | ' 
                notice_text(Token, "#stock_notice", attach_list)

        
        # notice_message(Token, "#stock_notice", str1_title, attach_list)
        # post_message(Token, "#stock_notice", attach_list)
        # notice_text(Token, "#stock_notice", attach_list)

schedule.every().day.at("07:00").do(job)
schedule.every().day.at("14:30").do(job)
# schedule.every(3).seconds.do(job) # 3초마다 job 실행

while True:
    schedule.run_pending()
    time.sleep(1)    
