# 1. Selenium의 필요한 모듈을 가져옴
from selenium import webdriver  # 브라우저를 제어하는 라이브러리
from selenium.webdriver.common.by import By  # HTML 요소를 찾을 때 사용
from selenium.webdriver.common.keys import Keys  # 키보드 입력을 자동화할 때 사용
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# 2. Chrome 브라우저 실행
driver = webdriver.Chrome()

# 3. 웹사이트 열기
driver.get("https://www.hanainsure.co.kr/w/disclosure/product/saleProduct")

time.sleep(1)

# # 4. 버튼을 찾고 클릭하기
# for i in range(3):
button = driver.find_element(By.XPATH, f"//a[@data-ins_type='2' and text()='장기보험']")
driver.execute_script("arguments[0].click();", button)
time.sleep(0.5)

for j in range(21,24):

    # <a href="javascript:void(0);" data-ins_type="0" data-ins_dtl_type="01" class="on">개인용</a>
    button = driver.find_element(By.XPATH, f"//a[@data-ins_type='2' and @data-ins_dtl_type='{j}']")
    driver.execute_script("arguments[0].click();", button)
    time.sleep(0.5)
    links = driver.find_elements(By.XPATH, "//div[@id='divStep02']//a")

    for i, link in enumerate(links):
        name = link.text     # 상품 목록을 순회하면서 클릭
        driver.execute_script("arguments[0].click();", link)
        time.sleep(0.1)

         # 판매 기간 '현재' 버튼 클릭
        button = driver.find_element(By.XPATH, "//div[@id='divStep03']//a[1]")
        driver.execute_script("arguments[0].click();", button)
        time.sleep(0.1)

        # 약관 보기 pdf 버튼 클릭
        button = driver.find_element(By.XPATH, "//div[@class='btn_group']/a[1]")
        driver.execute_script("arguments[0].click();", button)
        all_tabs = driver.window_handles  # 모든 탭의 핸들 리스트
        new_tab = all_tabs[1]  # 새 탭은 리스트에서 두 번째 탭
        driver.switch_to.window(new_tab) # 여기서 새 탭에서 할 작업을 수행할 수 있습니다.
        
        time.sleep(1.5)
        pdf_url = driver.current_url

        response = requests.get(pdf_url)
        file_name = f"./하나손해보험 약관파일/3_장기보험/{j}_{i+1}_{name}_pdf.pdf"
        with open(file_name, "wb") as f:
            f.write(response.content)
            time.sleep(0.1)

        driver.close()  # 현재 탭(새 탭) 닫기

        time.sleep(0.1)
        driver.switch_to.window(all_tabs[0])  # 다시 원래 첫 번째 탭으로 돌아가기

driver.quit()