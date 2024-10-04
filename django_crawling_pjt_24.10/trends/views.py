import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import Keyword, Trend
from bs4 import BeautifulSoup
from selenium import webdriver
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta


# Create your views here.
def keyword(request):
    if request.method == "POST":
        keyword_value = request.POST.get('keyword', '')
        if keyword_value:
            # 키워드를 모델에 저장
            new_keyword, created = Keyword.objects.get_or_create(keyword_text=keyword_value)
            if created:
                new_keyword.save()  # 데이터베이스에 저장

            # 저장 후 크롤링 함수 실행
            return crawling(request, [new_keyword])

        # 저장 후 다른 페이지로 리다이렉트하거나 메시지와 함께 렌더링
        return redirect('trends:keyword')  # POST 이후 GET 요청으로 리다이렉트
    
    # 저장된 키워드를 가져오기 (예: 최근 키워드)
    keywords = Keyword.objects.all()

    return render(request, 'trends/keyword.html', {'keywords': keywords})


def keyword_detail(request, keyword_pk):
    keyword = get_object_or_404(Keyword, pk=keyword_pk)
    keyword.delete()
    Trend.objects.filter(keyword=keyword).delete()  # 키워드와 관련된 Trend 데이터 삭제
    return redirect("trends:keyword")

# 크롤링 수행 및 Trend 테이블 업데이트 뷰
def crawling(request, keywords=None):
    # 크롤링할 URL 설정
    if not keywords:
        keywords = Keyword.objects.all()
    
    # 웹페이지 요청 및 크롤링
    try:
        for keyword in keywords:
            url = f"https://www.google.com/search?q={keyword.keyword_text}"
            response = requests.get(url)
            response.raise_for_status()  # 에러 발생 시 예외 처리
            soup = BeautifulSoup(response.text, 'html.parser')

            # 검색 결과 개수를 추출하는 로직 (예시로 검색 결과 개수를 가정)
            search_result_count = len(soup.find_all(text=lambda text: keyword.keyword_text.lower() in text.lower()))

            # Trend 테이블 업데이트 또는 생성
            trend, created = Trend.objects.get_or_create(keyword=keyword, search_period='all', defaults={'result_count': search_result_count, 'search_date': datetime.now()})
            if not created:
                trend.result_count = search_result_count
                trend.search_date = datetime.now()
                trend.save()

    except requests.exceptions.RequestException as e:
        context = {
            'page_title': "크롤링 에러",
            'error_message': str(e),
        }
        return render(request, 'trends/crawling.html', context)

    # 크롤링 결과를 템플릿에 전달
    keywords = Keyword.objects.all()
    trends = Trend.objects.filter(keyword__in=keywords)
    context = {
        'keywords': keywords,
        'trends': trends,
    }
    return render(request, 'trends/crawling.html', context)


def crawling_histogram(request):
    
    # Trend 테이블에 저장된 데이터를 사용하여 막대 그래프 생성
    trends = Trend.objects.all()
    keyword_texts = [trend.keyword.keyword_text for trend in trends]
    result_counts = [trend.result_count for trend in trends]

    # 막대 그래프 생성
    plt.figure(figsize=(10, 6))
    plt.bar(keyword_texts, result_counts, color='blue')
    plt.title('Keyword Trend Analysis')
    plt.xlabel('Keywords')
    plt.ylabel('Search Result Count')

    # 그래프를 메모리에 저장
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # 그래프를 base64로 인코딩하여 HTML로 전달
    graph = base64.b64encode(image_png).decode('utf-8')

    context = {
        'graph': graph,
    }
    return render(request, 'trends/crawling_histogram.html', context)

def crawling_advanced(request):
    if request.method == "POST":
        url = request.POST.get('url', 'https://example.com')
        one_year_ago = datetime.now() - timedelta(days=365)

        # 크롤링 작업
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 예를 들어, 지난 1년간의 특정 데이터(게시물 날짜 등)를 필터링한다고 가정
            dates = soup.find_all('time')  # 'time' 태그가 게시물 날짜를 나타낸다고 가정
            recent_counts = 0

            for date in dates:
                date_str = date.get('datetime')  # 'datetime' 속성에서 날짜 가져오기
                if date_str:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    if date_obj >= one_year_ago:
                        recent_counts += 1

            # 막대 그래프 생성 (지난 1년간 게시물 수)
            plt.figure(figsize=(10, 6))
            plt.bar(['Last Year'], [recent_counts], color='green')
            plt.title('Number of Posts in the Last Year')
            plt.xlabel('Time Period')
            plt.ylabel('Number of Posts')

            # 그래프를 메모리에 저장
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            # 그래프를 base64로 인코딩하여 HTML로 전달
            graph = base64.b64encode(image_png).decode('utf-8')

        except requests.exceptions.RequestException as e:
            graph = None

        context = {
            'graph': graph,
            'url': url,
        }
        return render(request, 'trends/crawling_advanced.html', context)

    # GET 요청일 경우 빈 폼 렌더링
    return render(request, 'trends/crawling_advanced.html')