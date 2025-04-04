# 각 보험별로 class 생성 및 크롤링
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# 일반보험 
class GeneralInsuranceScraper:
    def __init__(self):
        # 기본 다운로드 경로 설정
        self.base_download_path = os.path.abspath("SKN09-3rd-4Team/data/일반보험")
        os.makedirs(self.base_download_path, exist_ok=True)

        # 웹드라이버 실행
        self.driver = webdriver.Chrome(options=self.set_chrome_options())
        self.driver.get('https://www.kbinsure.co.kr/CG802030001.ec')

    def set_chrome_options(self):
        """Chrome 옵션 설정"""
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.base_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return chrome_options

    def select_and_click_button(self):
        """'일반보험'을 선택하고 조회 버튼을 클릭"""
        try:
            # <select> 요소 찾기
            section_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[1]/table/tbody/tr[1]//select'))
            )
            select_box = Select(section_element)
            select_box.select_by_value('Y')  # <option value='Y'> 선택
            print("<select> 요소에서 'Y' 값 선택 완료")

            # '일반보험' 요소 찾기
            section_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "search_gubun")))

            # Select 클래스를 사용하여 두 번째 옵션 선택
            select = Select(section_element)
            select.select_by_index(1)  # 두 번째 옵션 (index는 0부터 시작)
            print("<보험종류> 요소에서 '일반보험' 값 선택 완료")

            # 조회 버튼 클릭
            button_element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[2]//button'))
            )
            button_element.click()
            print("<button> 요소 클릭 완료")
            time.sleep(3)  # 버튼 클릭 후 페이지 로드 대기

        except Exception as e:
            print(f"Error during select and button click: {e}")

    def download_files_on_current_page(self):
        """현재 페이지에서 모든 파일 다운로드"""
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))
            rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')

            for i in range(len(rows)):
                try:
                    rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')
                    link = WebDriverWait(rows[i], 10).until(EC.element_to_be_clickable((By.XPATH, './/a')))
                    link.click()
                    print(f"Row {i+1} 클릭됨")
                    time.sleep(3)

                    pdf_link_xpath = '//*[@id="contents"]/div[1]/table/tbody/tr[2]/td/div/table/tbody/tr[last()]/td[3]//a'
                    pdf_link = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, pdf_link_xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", pdf_link)
                    time.sleep(2)
                    ActionChains(self.driver).move_to_element(pdf_link).click().perform()
                    print(f"Row {i+1} PDF 파일 다운로드 중...")
                    time.sleep(5)

                    back_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="contents"]/div[2]/a')))
                    back_button.click()
                    print("목록으로 돌아가기 클릭됨")
                    time.sleep(3)

                    WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))

                except Exception as e:
                    print(f"Error in row {i+1}: {e}")

        except Exception as e:
            print("Error loading page:", e)

    def navigate_pages(self):
        """페이지 이동 및 다운로드 실행"""
        try:
            # 처음에 한 번만 '판매중' 상품 선택 및 조회 버튼 클릭
            print("선택 및 조회")
            self.select_and_click_button()
            time.sleep(3)  # 페이지 로드 대기

            # 1페이지 처리
            print("1페이지 처리 중...")
            self.download_files_on_current_page()

            for page in range(2, 6 + 1):  # 2페이지부터 6페이지까지
                print(f"{page}페이지로 이동 시도")

                pagination_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[3]'))
                )
                page_links = pagination_div.find_elements(By.TAG_NAME, 'a')

                for link in page_links:
                    title = link.get_attribute('title')
                    if title and f"{page} 페이지로 이동" in title:
                        print(f"{page}페이지 링크 클릭")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        link.click()
                        time.sleep(5)  # 페이지 로드 대기

                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr'))
                        )
                        print(f"{page}페이지로 성공적으로 이동")

                        self.download_files_on_current_page()
                        break
                else:
                    print(f"{page}페이지 링크를 찾을 수 없음")
                    break

                time.sleep(2)

        except Exception as e:
            print(f"오류 발생: {e}")

    def run(self):
        """스크래핑 실행"""
        self.navigate_pages()

    def close(self):
        """웹드라이버 종료"""
        self.driver.quit()

# if __name__ == "__main__":
#     scraper = GeneralInsuranceScraper()
#     try:
#         scraper.run()
#     finally:
#         scraper.close()


# 자동차 보험
class CarInsuranceScraper:
    def __init__(self):
        # 기본 다운로드 경로 설정
        self.base_download_path = os.path.abspath("SKN09-3rd-4Team/data/자동차보험")
        os.makedirs(self.base_download_path, exist_ok=True)

        # 웹드라이버 실행
        self.driver = webdriver.Chrome(options=self.set_chrome_options())
        self.driver.get('https://www.kbinsure.co.kr/CG802030001.ec')

    def set_chrome_options(self):
        """Chrome 옵션 설정"""
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.base_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return chrome_options

    def select_and_click_button(self):
        """보험 선택하고 조회 버튼을 클릭"""
        try:
            # <select> 요소 찾기
            section_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[1]/table/tbody/tr[1]//select'))
            )
            select_box = Select(section_element)
            select_box.select_by_value('Y')  # <option value='Y'> 선택
            print("<select> 요소에서 'Y' 값 선택 완료")

            #보험 요소 찾기
            section_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "search_gubun")))

            # Select 클래스를 사용하여 옵션 선택
            select = Select(section_element)
            select.select_by_index(3)  
            print("<보험종류> 요소에서 값 선택 완료")

            # 조회 버튼 클릭
            button_element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[2]//button'))
            )
            button_element.click()
            print("<button> 요소 클릭 완료")
            time.sleep(3)  # 버튼 클릭 후 페이지 로드 대기

        except Exception as e:
            print(f"Error during select and button click: {e}")

    def download_files_on_current_page(self):
        """현재 페이지에서 모든 파일 다운로드"""
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))
            rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')

            for i in range(len(rows)):
                try:
                    rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')
                    link = WebDriverWait(rows[i], 10).until(EC.element_to_be_clickable((By.XPATH, './/a')))
                    link.click()
                    print(f"Row {i+1} 클릭됨")
                    time.sleep(3)

                    pdf_link_xpath = '//*[@id="contents"]/div[1]/table/tbody/tr[3]/td/div/table/tbody/tr[last()]/td[3]//a'
                    pdf_link = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, pdf_link_xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", pdf_link)
                    time.sleep(2)
                    ActionChains(self.driver).move_to_element(pdf_link).click().perform()
                    print(f"Row {i+1} PDF 파일 다운로드 중...")
                    time.sleep(5)

                    back_button = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="contents"]/div[2]/a')))
                    back_button.click()
                    print("목록으로 돌아가기 클릭됨")
                    time.sleep(3)

                    WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))

                except Exception as e:
                    print(f"Error in row {i+1}: {e}")

        except Exception as e:
            print("Error loading page:", e)

    def navigate_pages(self):
        """페이지 이동 및 다운로드 실행"""
        try:
            # 처음에 한 번만 '판매중' 상품 선택 및 조회 버튼 클릭
            print("선택 및 조회")
            self.select_and_click_button()
            time.sleep(3)  # 페이지 로드 대기

            # 1페이지 처리
            print("1페이지 처리 중...")
            self.download_files_on_current_page()

            for page in range(2, 4 + 1):  # 2페이지부터 6페이지까지
                print(f"{page}페이지로 이동 시도")

                pagination_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[3]'))
                )
                page_links = pagination_div.find_elements(By.TAG_NAME, 'a')

                for link in page_links:
                    title = link.get_attribute('title')
                    if title and f"{page} 페이지로 이동" in title:
                        print(f"{page}페이지 링크 클릭")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        link.click()
                        time.sleep(5)  # 페이지 로드 대기

                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr'))
                        )
                        print(f"{page}페이지로 성공적으로 이동")

                        self.download_files_on_current_page()
                        break
                else:
                    print(f"{page}페이지 링크를 찾을 수 없음")
                    break

                time.sleep(2)

        except Exception as e:
            print(f"오류 발생: {e}")

    def run(self):
        """스크래핑 실행"""
        self.navigate_pages()

    def close(self):
        """웹드라이버 종료"""
        self.driver.quit()


# 자동차 보험
class CarInsuranceScraper:
    def __init__(self):
        # 기본 다운로드 경로 설정
        self.base_download_path = os.path.abspath("SKN09-3rd-4Team/data/자동차보험")
        os.makedirs(self.base_download_path, exist_ok=True)

        # 웹드라이버 실행
        self.driver = webdriver.Chrome(options=self.set_chrome_options())
        self.driver.get('https://www.kbinsure.co.kr/CG802030001.ec')

    def set_chrome_options(self):
        """Chrome 옵션 설정"""
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.base_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return chrome_options

    def select_and_click_button(self):
        """보험 선택하고 조회 버튼을 클릭"""
        try:
            # <select> 요소 찾기
            section_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[1]/table/tbody/tr[1]//select'))
            )
            select_box = Select(section_element)
            select_box.select_by_value('Y')  # <option value='Y'> 선택
            print("<select> 요소에서 'Y' 값 선택 완료")

            #보험 요소 찾기
            section_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "search_gubun")))

            # Select 클래스를 사용하여 옵션 선택
            select = Select(section_element)
            select.select_by_index(3)  
            print("<보험종류> 요소에서 값 선택 완료")

            # 조회 버튼 클릭
            button_element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[2]//button'))
            )
            button_element.click()
            print("<button> 요소 클릭 완료")
            time.sleep(3)  # 버튼 클릭 후 페이지 로드 대기

        except Exception as e:
            print(f"Error during select and button click: {e}")

    def download_files_on_current_page(self):
        """현재 페이지에서 모든 파일 다운로드"""
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))
            rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')

            for i in range(len(rows)):
                try:
                    rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')
                    link = WebDriverWait(rows[i], 10).until(EC.element_to_be_clickable((By.XPATH, './/a')))
                    link.click()
                    print(f"Row {i+1} 클릭됨")
                    time.sleep(3)

                    pdf_link_xpath = '//*[@id="contents"]/div[1]/table/tbody/tr[3]/td/div/table/tbody/tr[last()]/td[3]//a'
                    pdf_link = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, pdf_link_xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", pdf_link)
                    time.sleep(2)
                    ActionChains(self.driver).move_to_element(pdf_link).click().perform()
                    print(f"Row {i+1} PDF 파일 다운로드 중...")
                    time.sleep(5)

                    back_button = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="contents"]/div[2]/a')))
                    back_button.click()
                    print("목록으로 돌아가기 클릭됨")
                    time.sleep(3)

                    WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))

                except Exception as e:
                    print(f"Error in row {i+1}: {e}")

        except Exception as e:
            print("Error loading page:", e)

    def navigate_pages(self):
        """페이지 이동 및 다운로드 실행"""
        try:
            # 처음에 한 번만 '판매중' 상품 선택 및 조회 버튼 클릭
            print("선택 및 조회")
            self.select_and_click_button()
            time.sleep(3)  # 페이지 로드 대기

            # 1페이지 처리
            print("1페이지 처리 중...")
            self.download_files_on_current_page()

            for page in range(2, 4 + 1):  # 2페이지부터 6페이지까지
                print(f"{page}페이지로 이동 시도")

                pagination_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[3]'))
                )
                page_links = pagination_div.find_elements(By.TAG_NAME, 'a')

                for link in page_links:
                    title = link.get_attribute('title')
                    if title and f"{page} 페이지로 이동" in title:
                        print(f"{page}페이지 링크 클릭")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        link.click()
                        time.sleep(5)  # 페이지 로드 대기

                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr'))
                        )
                        print(f"{page}페이지로 성공적으로 이동")

                        self.download_files_on_current_page()
                        break
                else:
                    print(f"{page}페이지 링크를 찾을 수 없음")
                    break

                time.sleep(2)

        except Exception as e:
            print(f"오류 발생: {e}")

    def run(self):
        """스크래핑 실행"""
        self.navigate_pages()

    def close(self):
        """웹드라이버 종료"""
        self.driver.quit()

# if __name__ == "__main__":
#     scraper = CarInsuranceScraper()
#     try:
#         scraper.run()
#     finally:
#         scraper.close()


# 상해보험
class AccidentInsurance:
    def __init__(self):
        # 기본 다운로드 경로 설정
        self.base_download_path = os.path.abspath("SKN09-3rd-4Team/data/상해보험")
        os.makedirs(self.base_download_path, exist_ok=True)

        # 웹드라이버 실행
        self.driver = webdriver.Chrome(options=self.set_chrome_options())
        self.driver.get('https://www.kbinsure.co.kr/CG802030001.ec')

    def set_chrome_options(self):
        """Chrome 옵션 설정"""
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.base_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return chrome_options

    def select_and_click_button(self):
        """보험 선택하고 조회 버튼을 클릭"""
        try:
            # <select> 요소 찾기
            section_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[1]/table/tbody/tr[1]//select'))
            )
            select_box = Select(section_element)
            select_box.select_by_value('Y')  # <option value='Y'> 선택
            print("<select> 요소에서 'Y' 값 선택 완료")

            #보험 요소 찾기
            section_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "search_gubun")))

            # Select 클래스를 사용하여 옵션 선택
            select = Select(section_element)
            select.select_by_index(9)  
            print("<보험종류> 요소에서 값 선택 완료")

            # 조회 버튼 클릭
            button_element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[2]//button'))
            )
            button_element.click()
            print("<button> 요소 클릭 완료")
            time.sleep(3)  # 버튼 클릭 후 페이지 로드 대기

        except Exception as e:
            print(f"Error during select and button click: {e}")

    def download_files_on_current_page(self):
        """현재 페이지에서 모든 파일 다운로드"""
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))
            rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')

            for i in range(len(rows)):
                try:
                    rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')
                    link = WebDriverWait(rows[i], 10).until(EC.element_to_be_clickable((By.XPATH, './/a')))
                    link.click()
                    print(f"Row {i+1} 클릭됨")
                    time.sleep(3)

                    pdf_link_xpath = '//*[@id="contents"]/div[1]/table/tbody/tr[2]/td/div/table/tbody/tr[last()]/td[3]//a'
                    pdf_link = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, pdf_link_xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", pdf_link)
                    time.sleep(2)
                    ActionChains(self.driver).move_to_element(pdf_link).click().perform()
                    print(f"Row {i+1} PDF 파일 다운로드 중...")
                    time.sleep(5)

                    back_button = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="contents"]/div[2]/a')))
                    back_button.click()
                    print("목록으로 돌아가기 클릭됨")
                    time.sleep(3)

                    WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))

                except Exception as e:
                    print(f"Error in row {i+1}: {e}")

        except Exception as e:
            print("Error loading page:", e)

    def navigate_pages(self):
        """페이지 이동 및 다운로드 실행"""
        try:
            # 처음에 한 번만 '판매중' 상품 선택 및 조회 버튼 클릭
            print("선택 및 조회")
            self.select_and_click_button()
            time.sleep(3)  # 페이지 로드 대기

            # 1페이지 처리
            print("1페이지 처리 중...")
            self.download_files_on_current_page()

            for page in range(2, 5 + 1):  # 2페이지부터 6페이지까지
                print(f"{page}페이지로 이동 시도")

                pagination_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[3]'))
                )
                page_links = pagination_div.find_elements(By.TAG_NAME, 'a')

                for link in page_links:
                    title = link.get_attribute('title')
                    if title and f"{page} 페이지로 이동" in title:
                        print(f"{page}페이지 링크 클릭")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        link.click()
                        time.sleep(5)  # 페이지 로드 대기

                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr'))
                        )
                        print(f"{page}페이지로 성공적으로 이동")

                        self.download_files_on_current_page()
                        break
                else:
                    print(f"{page}페이지 링크를 찾을 수 없음")
                    break

                time.sleep(2)

        except Exception as e:
            print(f"오류 발생: {e}")

    def run(self):
        """스크래핑 실행"""
        self.navigate_pages()

    def close(self):
        """웹드라이버 종료"""
        self.driver.quit()

# if __name__ == "__main__":
#     scraper = AccidentInsurance()
#     try:
#         scraper.run()
#     finally:
#         scraper.close()


# 제휴
class Affiliate:
    def __init__(self):
        # 기본 다운로드 경로 설정
        self.base_download_path = os.path.abspath("SKN09-3rd-4Team/data/제휴")
        os.makedirs(self.base_download_path, exist_ok=True)

        # 웹드라이버 실행
        self.driver = webdriver.Chrome(options=self.set_chrome_options())
        self.driver.get('https://www.kbinsure.co.kr/CG802030001.ec')

    def set_chrome_options(self):
        """Chrome 옵션 설정"""
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.base_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return chrome_options

    def select_and_click_button(self):
        """보험 선택하고 조회 버튼을 클릭"""
        try:
            # <select> 요소 찾기
            section_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[1]/table/tbody/tr[1]//select'))
            )
            select_box = Select(section_element)
            select_box.select_by_value('Y')  # <option value='Y'> 선택
            print("<select> 요소에서 'Y' 값 선택 완료")

            #보험 요소 찾기
            section_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "search_gubun")))

            # Select 클래스를 사용하여 옵션 선택
            select = Select(section_element)
            select.select_by_index(13)  
        
            print("<보험종류> 요소에서 값 선택 완료")

            # 조회 버튼 클릭
            button_element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[2]//button'))
            )
            button_element.click()
            print("<button> 요소 클릭 완료")
            time.sleep(3)  # 버튼 클릭 후 페이지 로드 대기

        except Exception as e:
            print(f"Error during select and button click: {e}")

    def download_files_on_current_page(self):
        """현재 페이지에서 모든 파일 다운로드"""
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))
            rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')

            for i in range(len(rows)):
                try:
                    rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')
                    link = WebDriverWait(rows[i], 10).until(EC.element_to_be_clickable((By.XPATH, './/a')))
                    link.click()
                    print(f"Row {i+1} 클릭됨")
                    time.sleep(3)

                    pdf_link_xpath = '//*[@id="contents"]/div[1]/table/tbody/tr[2]/td/div/table/tbody/tr[last()]/td[3]//a'
                    pdf_link = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, pdf_link_xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", pdf_link)
                    time.sleep(2)
                    ActionChains(self.driver).move_to_element(pdf_link).click().perform()
                    print(f"Row {i+1} PDF 파일 다운로드 중...")
                    time.sleep(5)

                    back_button = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="contents"]/div[2]/a')))
                    back_button.click()
                    print("목록으로 돌아가기 클릭됨")
                    time.sleep(3)

                    WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))

                except Exception as e:
                    print(f"Error in row {i+1}: {e}")

        except Exception as e:
            print("Error loading page:", e)

    def navigate_pages(self):
        """페이지 이동 및 다운로드 실행"""
        try:
            # 처음에 한 번만 '판매중' 상품 선택 및 조회 버튼 클릭
            print("선택 및 조회")
            self.select_and_click_button()
            time.sleep(3)  # 페이지 로드 대기

            # 1페이지 처리
            print("1페이지 처리 중...")
            self.download_files_on_current_page()

            for page in range(2, 5 + 1):  # 2페이지부터 6페이지까지
                print(f"{page}페이지로 이동 시도")

                pagination_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[3]'))
                )
                page_links = pagination_div.find_elements(By.TAG_NAME, 'a')

                for link in page_links:
                    title = link.get_attribute('title')
                    if title and f"{page} 페이지로 이동" in title:
                        print(f"{page}페이지 링크 클릭")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        link.click()
                        time.sleep(5)  # 페이지 로드 대기

                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr'))
                        )
                        print(f"{page}페이지로 성공적으로 이동")

                        self.download_files_on_current_page()
                        break
                else:
                    print(f"{page}페이지 링크를 찾을 수 없음")
                    break

                time.sleep(2)

        except Exception as e:
            print(f"오류 발생: {e}")

    def run(self):
        """스크래핑 실행"""
        self.navigate_pages()

    def close(self):
        """웹드라이버 종료"""
        self.driver.quit()


# 제도성 특별약관
class SystemicSpecial:
    def __init__(self):
        # 기본 다운로드 경로 설정
        self.base_download_path = os.path.abspath("SKN09-3rd-4Team/data/제도성 특별약관")
        os.makedirs(self.base_download_path, exist_ok=True)

        # 웹드라이버 실행
        self.driver = webdriver.Chrome(options=self.set_chrome_options())
        self.driver.get('https://www.kbinsure.co.kr/CG802030001.ec')

    def set_chrome_options(self):
        """Chrome 옵션 설정"""
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.base_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return chrome_options

    def select_and_click_button(self):
        """보험 선택하고 조회 버튼을 클릭"""
        try:
            # <select> 요소 찾기
            section_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[1]/table/tbody/tr[1]//select'))
            )
            select_box = Select(section_element)
            select_box.select_by_value('Y')  # <option value='Y'> 선택
            print("<select> 요소에서 'Y' 값 선택 완료")

            #보험 요소 찾기
            section_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "search_gubun")))

            # Select 클래스를 사용하여 옵션 선택
            select = Select(section_element)
            select.select_by_index(17-1)  
            print("<보험종류> 요소에서 값 선택 완료")

            # 조회 버튼 클릭
            button_element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[2]//button'))
            )
            button_element.click()
            print("<button> 요소 클릭 완료")
            time.sleep(3)  # 버튼 클릭 후 페이지 로드 대기

        except Exception as e:
            print(f"Error during select and button click: {e}")

    def download_files_on_current_page(self):
        """현재 페이지에서 모든 파일 다운로드"""
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))
            rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')

            for i in range(len(rows)):
                try:
                    rows = self.driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')
                    link = WebDriverWait(rows[i], 10).until(EC.element_to_be_clickable((By.XPATH, './/a')))
                    link.click()
                    print(f"Row {i+1} 클릭됨")
                    time.sleep(3)

                    pdf_link_xpath = '//*[@id="contents"]/div[1]/table/tbody/tr[2]/td/div/table/tbody/tr[last()]/td[3]//a'
                    pdf_link = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, pdf_link_xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", pdf_link)
                    time.sleep(2)
                    ActionChains(self.driver).move_to_element(pdf_link).click().perform()
                    print(f"Row {i+1} PDF 파일 다운로드 중...")
                    time.sleep(5)

                    back_button = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="contents"]/div[2]/a')))
                    back_button.click()
                    print("목록으로 돌아가기 클릭됨")
                    time.sleep(3)

                    WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))

                except Exception as e:
                    print(f"Error in row {i+1}: {e}")

        except Exception as e:
            print("Error loading page:", e)

    def navigate_pages(self):
        """페이지 이동 및 다운로드 실행"""
        try:
            # 처음에 한 번만 '판매중' 상품 선택 및 조회 버튼 클릭
            print("선택 및 조회")
            self.select_and_click_button()
            time.sleep(3)  # 페이지 로드 대기

            # 1페이지 처리
            print("1페이지 처리 중...")
            self.download_files_on_current_page()

            for page in range(2, 5 + 1):  # 2페이지부터 6페이지까지
                print(f"{page}페이지로 이동 시도")

                pagination_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[3]'))
                )
                page_links = pagination_div.find_elements(By.TAG_NAME, 'a')

                for link in page_links:
                    title = link.get_attribute('title')
                    if title and f"{page} 페이지로 이동" in title:
                        print(f"{page}페이지 링크 클릭")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        link.click()
                        time.sleep(5)  # 페이지 로드 대기

                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr'))
                        )
                        print(f"{page}페이지로 성공적으로 이동")

                        self.download_files_on_current_page()
                        break
                else:
                    print(f"{page}페이지 링크를 찾을 수 없음")
                    break

                time.sleep(2)

        except Exception as e:
            print(f"오류 발생: {e}")

    def run(self):
        """스크래핑 실행"""
        self.navigate_pages()

    def close(self):
        """웹드라이버 종료"""
        self.driver.quit()


if __name__ == "__main__":
    scraper = SystemicSpecial()
    try:
        scraper.run()
    finally:
        scraper.close()






# 실패 코드 
    # search_gubun = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.ID, 'search_gubun'))
    # )
    # search_gubun_options = Select(search_gubun).options

#     # 2번째 옵션부터 순회
#     for option_index in range(2, len(search_gubun_options)):
#         while True:
#             try:
#                 # search_gubun의 현재 옵션 선택
#                 search_gubun = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.ID, 'search_gubun'))
#                 )
#                 Select(search_gubun).select_by_index(option_index)
                
#                 # 선택된 옵션의 텍스트 추출
#                 selected_option = search_gubun.find_element(By.XPATH, ".//option[@selected]")
#                 selected_text = selected_option.text.strip()
                
#                 print(f"search_gubun 옵션 선택: {selected_text}")

#                 # 조회 버튼 클릭
#                 button_element = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.XPATH, '//*[@id="prdtList"]/div[1]/table/tbody/tr/td[2]//button'))
#                 )
#                 button_element.click()
#                 print("<button> 요소 클릭 완료")
#                 time.sleep(3)  # 버튼 클릭 후 페이지 로드 대기

#                 # tbody 내부의 tr 요소들 대기 후 찾기
#                 WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))
#                 rows = driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')

#                 if not rows:
#                     print(f"'{selected_text}' 옵션에 대한 결과가 없습니다. 다음 옵션으로 넘어갑니다.")
#                     break

#                 for i in range(len(rows)):
#                     try:
#                         # 매번 새로운 elements 리스트를 가져오기 (StaleElementReferenceException 방지)
#                         rows = driver.find_elements(By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')

#                         # tr 내부의 a 태그 클릭
#                         link = WebDriverWait(rows[i], 10).until(EC.element_to_be_clickable((By.XPATH, './/a')))
#                         link.click()
#                         print(f"Row {i+1} 클릭됨")
#                         time.sleep(3)  # 클릭 후 페이지 변화를 볼 수 있도록 3초 대기

#                         # 새 페이지에서 마지막 tr의 PDF 다운로드 링크 찾기 및 클릭
#                         pdf_link_xpath = '//*[@id="contents"]/div[1]/table/tbody/tr[2]/td/div/table/tbody/tr[last()]/td[3]//a'
#                         pdf_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, pdf_link_xpath)))
#                         driver.execute_script("arguments[0].scrollIntoView(true);", pdf_link)
#                         time.sleep(2)
#                         ActionChains(driver).move_to_element(pdf_link).click().perform()
#                         print(f"Row {i+1} PDF 파일 다운로드 중...")
#                         time.sleep(5)  # 다운로드 대기

#                         # "목록으로 돌아가기" 버튼이 나타날 때까지 대기
#                         back_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="contents"]/div[2]/a')))
#                         back_button.click()
#                         print("목록으로 돌아가기 클릭됨")
#                         time.sleep(5)  # 목록 페이지로 돌아오는 걸 볼 수 있도록 5초 대기

#                         # 목록 페이지 로드 대기
#                         WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prdtList"]/div[2]/table/tbody/tr')))

#                     except NoSuchElementException:
#                         print(f"Row {i+1}에서 a 태그를 찾을 수 없습니다. 다음 옵션으로 넘어갑니다.")
#                         break

#                     except Exception as e:
#                         print(f"Error in row {i+1}: {e}")

#                 break  # 모든 행을 처리했거나 a 태그가 없는 경우 while 루프 종료

#             except StaleElementReferenceException:
#                 print("StaleElementReferenceException 발생, 요소 다시 찾기")
#                 continue

#             except Exception as e:
#                 print("Error loading page:", e)
#                 break

# except Exception as e:
#     print(f"Error during select and button click: {e}")

# # 드라이버 종료
# driver.quit()


