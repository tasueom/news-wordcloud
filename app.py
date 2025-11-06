from flask import Flask, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
import os, re
from collections import Counter

app = Flask(__name__)

def not_a_robot():
    # ▶ 웹 요청 시, 브라우저처럼 보이게 하기 위한 HTTP 헤더 설정
    #   (requests로 직접 접속하면 '봇'으로 차단당할 수 있으므로)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    return headers

def get_news_content(news_link):
    # URL에 프로토콜이 없으면 https:// 추가
    if not news_link.startswith(("http://", "https://")):
        news_link = "https://" + news_link
    
    response = requests.get(news_link, headers=not_a_robot())
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find(class_='newsct_article _article_body').text

def get_data(news_content):
    # 한글, 영어, 공백만 남기고 나머지 제거
    news_content = re.sub(r"[^가-힣a-zA-Z\s]", "", news_content)
    # 단어 분리
    words = news_content.split()
    # 불용어 제거
    stop_words = ["그리고", "에서", "를", "이", "은", "는", "도", "에", "으로", "합니다", "합니다."]
    filtered = [word for word in words if word not in stop_words]
    # 단어 빈도 계산
    word_count = Counter(filtered)
    
    # 상위 10개 단어만 선택
    top_words = dict(word_count.most_common(10))
    labels = list(top_words.keys())
    values = list(top_words.values())

    # 워드클라우드용 전체 단어 리스트 (빈도 포함)
    wc_data = [{"text": w, "weight": c} for w, c in word_count.items()]

    return labels, values, wc_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    news_link = request.form['news_link']
    news_content = get_news_content(news_link)
    
    labels, values, wc_data = get_data(news_content)
    
    return render_template('result.html', labels=labels, values=values, wc_data=wc_data)

if __name__ == '__main__':
    app.run(debug=True)