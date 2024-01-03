# Slacker_notice_functions.py

from bs4 import BeautifulSoup
import requests
import json

def KospiRead():
    '''
    오늘의 KOSPI 관련 정보를 알려주는 함수. \n
    리턴 값 목록 : 
    1. trend_value : 투자자별, 프로그램 매매동향 값
    2. s : 코스피 차트 이미지 주소 (장시간동안 변화)
    3. a3 : 오늘의 KOSPI 값 / 등락값 / 등락률 값 (문자열)
    '''

    url = 'https://finance.naver.com/sise/sise_index.naver?code=KOSPI'
    # 네이버 금융이 헤더를 요구하는 방식으로 바뀌었다. 그래서 헤더가 필요하다.
    # headers = {' '}
    headers = {'Content-Type': 'application/soap+xml', 'charset': 'utf-8'}
    req = requests.get(url, headers = headers)

    soup = BeautifulSoup(req.text, 'lxml')
    daily = soup.find('div', class_ = 'graph')
    s = str(daily.img['src']) # 코스피 이미지 파일 주소.

    posts = soup.find('dl', class_ = 'lst_kos_info')
    post_title_1 = posts.find("dt").get_text() # 투자자별 매매동향
    post_title_2 = posts.find("dt", class_ = "last").get_text() # 프로그램별 매매동향

    trend_value = [] # 개인 , 외국인, 기관, 차익, 비차익, 전체
    characters = ",억" # 억으로 표기된 글자를 지우기 위해서 만듬
    operator = []
    i = 0

    for td in posts.parent.find_all('dd'):
        if td.text.find('+') != -1: # 양수
            operator.append('+')
        else: # -1 이 나온경우. 음수임.
            operator.append('-')
        refined_text = ''.join(x for x in str(td.text) if x not in characters)
        trend_value.append(str(refined_text.split(operator[i])[1]))
        trend_value[i] = operator[i] + trend_value[i]
        i = i + 1

    daily2 = soup.find('div', id = "quotient").get_text()
    a1 = daily2.split('\n')
    a2 = a1[2].split('%')[0]
    
    if a2.find('+') != -1: # + 인 경우
        a4 = '△'
    else:
        a4 = '▽'

    a3 = []
    a3.append(a1[1] + ' ')
    a3.append(a4 + a2 + '%')

    return s, trend_value, a3


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