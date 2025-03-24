from selenium import webdriver
from selenium.webdriver.common.by import By     # 태그 조회 방식
from selenium.common.exceptions import NoSuchElementException
import time
import os

# 다운로드 경로
download_dir = "D:\\study\sknetworks\\team_project\\pdf_folder"

options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {
    "download.default_directory": download_dir, #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
})

driver = webdriver.Chrome(options=options)

driver.get('https://www.lotteins.co.kr/web/C/D/H/cdh190.jsp#!')
time.sleep(1) # 웹페이지 로딩 시간을 기다려주기 위해 대기

def rename_latest_file(download_dir, new_name):
    files = os.listdir(download_dir)
    files = [f for f in files if f.endswith(".pdf")]  # PDF 파일만 필터링
    files.sort(key=lambda x: os.path.getctime(os.path.join(download_dir, x)), reverse=True)  # 최신 파일 찾기

    if files:
        latest_file = os.path.join(download_dir, files[0])
        new_file_path = os.path.join(download_dir, new_name)

        # 파일 이름 변경
        os.rename(latest_file, new_file_path)
        print(f"파일 이름 변경: {latest_file} → {new_file_path}")


# 자동차 보험
for i in range(1, 12):
    xpath_1 = f"/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[1]/ul/li[1]/ol/li[{i}]/a"
    btn_1 = driver.find_element(By.XPATH,xpath_1)
    btn_1.click()
    time.sleep(1)
    name_txt1 = driver.find_element(By.XPATH,xpath_1).text

    for j in range(1,100):
        xpath_2 = f"/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[2]/div/ul/li[{j}]/a"
        try:
            btn_2 = driver.find_element(By.XPATH, xpath_2)
            btn_2.click()
            time.sleep(1)
            name_txt2 = driver.find_element(By.XPATH,xpath_2).text
            name_txt2 = name_txt2.replace(":"," ")
            name_txt2 = name_txt2.replace("/"," ")

        except NoSuchElementException:
            continue

        if driver.find_element(By.XPATH,xpath_2):
            xpath_3 = "/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[3]/div/ul/li[1]/a/span"
            try:
                btn_3 = driver.find_element(By.XPATH, xpath_3)
                btn_3.click()
                time.sleep(1)

                xpath_4="/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[4]/div/ul/li[3]/a"
                btn_4 = driver.find_element(By.XPATH, xpath_4)
                btn_4.click()
                time.sleep(4)

                new_file_name = name_txt1 + "_" + name_txt2 + ".pdf"
                rename_latest_file(download_dir, new_file_name)

            except NoSuchElementException:
                continue
# 일반보험
xpath_1 = f"/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[1]/ul/li[2]/ol/li/a"
btn_1 = driver.find_element(By.XPATH,xpath_1)
btn_1.click()
time.sleep(1)
name_txt1 = driver.find_element(By.XPATH,xpath_1).text

for j in range(1,100):
    xpath_2 = f"/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[2]/div/ul/li[{j}]/a"
    try:
        btn_2 = driver.find_element(By.XPATH, xpath_2)
        btn_2.click()
        time.sleep(1)
        name_txt2 = driver.find_element(By.XPATH,xpath_2).text
        name_txt2 = name_txt2.replace(":"," ")
        name_txt2 = name_txt2.replace("/"," ")
        
    except NoSuchElementException:
        continue

    if driver.find_element(By.XPATH,xpath_2):
        xpath_3 = "/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[3]/div/ul/li[1]/a/span"
        try:
            btn_3 = driver.find_element(By.XPATH, xpath_3)
            btn_3.click()
            time.sleep(1)

            xpath_4="/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[4]/div/ul/li[3]/a"
            btn_4 = driver.find_element(By.XPATH, xpath_4)
            btn_4.click()
            time.sleep(4)

            new_file_name = name_txt1 + "_" + name_txt2 + ".pdf"
            rename_latest_file(download_dir, new_file_name)

        except NoSuchElementException:
            continue

# 장기보험
for i in range(1, 7):
    xpath_1 = f"/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[1]/ul/li[3]/ol/li[{i}]/a"
    btn_1 = driver.find_element(By.XPATH,xpath_1)
    btn_1.click()
    time.sleep(1)
    name_txt1 = driver.find_element(By.XPATH,xpath_1).text

    for j in range(1,100):
        xpath_2 = f"/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[2]/div/ul/li[{j}]/a"
        try:
            btn_2 = driver.find_element(By.XPATH, xpath_2)
            btn_2.click()
            time.sleep(1)
            name_txt2 = driver.find_element(By.XPATH,xpath_2).text
            name_txt2 = name_txt2.replace(":"," ")
            name_txt2 = name_txt2.replace("/"," ")

        except NoSuchElementException:
            continue

        if driver.find_element(By.XPATH,xpath_2):
            xpath_3 = "/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[3]/div/ul/li[1]/a/span"
            try:
                btn_3 = driver.find_element(By.XPATH, xpath_3)
                btn_3.click()
                time.sleep(1)

                xpath_4="/html/body/div[1]/div[2]/div[2]/div/form/div[3]/div/div/table/tbody/tr/td[4]/div/ul/li[3]/a"
                btn_4 = driver.find_element(By.XPATH, xpath_4)
                btn_4.click()
                time.sleep(4)
                
                new_file_name = name_txt1 + "_" + name_txt2 + ".pdf"
                rename_latest_file(download_dir, new_file_name)

            except NoSuchElementException:
                continue

driver.quit()