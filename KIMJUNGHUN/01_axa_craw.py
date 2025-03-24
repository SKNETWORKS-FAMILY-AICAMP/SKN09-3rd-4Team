from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import requests
import re

# AXA 약관 페이지 URL
URL = "https://www.axa.co.kr/AsianPlatformInternet/html/axacms/common/intro/disclosure/insurance/onsale_01.html"

# 웹드라이버 실행 (크롬 드라이버 필요)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

# AXA 약관 페이지 로드
driver.get(URL)
wait = WebDriverWait(driver, 10)

# PDF 저장 폴더 생성
pdf_folder = "axa_pdfs"
os.makedirs(pdf_folder, exist_ok=True)

# 중복 다운로드 방지를 위한 저장소
downloaded_pdfs = set()
downloaded_urls = set()
file_counter = 1  # 파일 순서 번호
MAX_DOWNLOADS = 39  # 다운로드 개수 제한

# 강제 클릭 함수
def force_click(element):
    try:
        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(1)
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)

# 파일명 정리 함수 (영어, 숫자만 유지, 언더스코어 제거)
def clean_filename(text):
    return re.sub(r'[^A-Za-z0-9]', '', text)

# 파일 다운로드 함수
def download_pdf(pdf_url, filename):
    global file_counter
    if pdf_url in downloaded_urls:
        print(f"이미 다운로드된 파일 (중복 스킵): {filename}")
        return

    pdf_filename = f"{file_counter:03d}{filename}.pdf"  # 파일명 앞에 숫자 추가, 언더스코어 제거
    pdf_path = os.path.join(pdf_folder, pdf_filename)

    print(f"다운로드 중: {pdf_filename}")

    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.get(pdf_url, stream=True, timeout=10)
            response.raise_for_status()

            with open(pdf_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)

            print(f"다운로드 완료: {pdf_filename}")
            downloaded_pdfs.add(pdf_filename)
            downloaded_urls.add(pdf_url)
            file_counter += 1  # 파일 순서 증가

            # 파일이 39개 다운로드되면 크롤링 종료
            if len(downloaded_pdfs) >= MAX_DOWNLOADS:
                print("최대 다운로드 개수(39개) 도달. 크롤링 종료.")
                driver.quit()
                exit()

            return

        except requests.exceptions.RequestException as e:
            print(f"다운로드 실패: {pdf_url} (재시도 {retry_count + 1}/{max_retries})")
            print(f"오류: {e}")
            retry_count += 1
            time.sleep(2)

# 상품 종류 리스트 가져오기
category_elements = driver.find_elements(By.CSS_SELECTOR, ".subTab li a")
category_dict = {cat.text.strip(): cat for cat in category_elements}

# 상품 종류 순회
for category_name, category_element in category_dict.items():
    print(f"상품 종류 선택: {category_name}")
    try:
        force_click(category_element)
        time.sleep(2)
    except Exception as e:
        print(f"상품 '{category_name}' 클릭 실패: {e}")
        continue

    # 보험 상품 리스트 가져오기
    product_elements = driver.find_elements(By.CSS_SELECTOR, ".prod_list .prod li a")
    product_dict = {prod.text.strip(): prod for prod in product_elements}

    # 각 보험 상품 순회
    for product_name, product_element in product_dict.items():
        print(f"보험 상품 선택: {product_name}")

        try:
            force_click(product_element)
            time.sleep(2)
        except Exception as e:
            print(f"보험 상품 '{product_name}' 클릭 실패: {e}")
            continue

        # 페이지 HTML 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 다운로드 테이블에서 '약관' PDF 링크 찾기
        download_table = soup.select(".down_tbl table tbody tr")
        for row in download_table:
            columns = row.find_all("td")
            if len(columns) < 4:
                continue

            # '현재' 포함된 판매 시기만 다운로드
            sales_period = columns[1].text.strip()
            if "현재" in sales_period:
                pdf_link_element = columns[3].find("a")
                if pdf_link_element and pdf_link_element.get("href"):
                    pdf_url = pdf_link_element["href"]
                    pdf_url = f"https://www.axa.co.kr{pdf_url}" if pdf_url.startswith("/") else pdf_url

                    # 파일명: 상품명 + 판매 시기 (YYYYMMDD)
                    cleaned_product_name = clean_filename(product_name)
                    cleaned_sales_period = re.sub(r'[^0-9]', '', sales_period)  # 숫자만 남김
                    filename = f"{cleaned_product_name}{cleaned_sales_period}"

                    download_pdf(pdf_url, filename)

# 드라이버 종료
driver.quit()

# 다운로드된 PDF 목록 저장
download_list_path = os.path.join(pdf_folder, "downloaded_pdfs.txt")
with open(download_list_path, "w", encoding="utf-8") as f:
    for pdf in downloaded_pdfs:
        f.write(pdf + "\n")

# 결과 출력
print(f"\n총 {len(downloaded_pdfs)}개의 PDF를 다운로드 완료했습니다.")
print(f"다운로드된 파일 목록은 {download_list_path}에 저장되었습니다.")

