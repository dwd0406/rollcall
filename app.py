from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging
import time
from bs4 import BeautifulSoup
import random
from selenium.common.exceptions import NoSuchElementException
# 'https://irs.zuvio.com.tw/student5/irs/rollcall/XXXXXX'
CHROME_DRIVER_PATH = ''  # 輸入你的chromedriver路徑

def login(driver, log_text, account, password):
    driver.get("https://irs.zuvio.com.tw/") # 首頁
    driver.find_element(By.ID, "email").send_keys(account)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-btn").submit()
    try:
        errmsg = driver.find_element(By.CLASS_NAME, "err_msg").text # 錯誤訊息
        log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M')} {errmsg}") # 輸出錯誤訊息
        return False
    except NoSuchElementException:# 找不到錯誤訊息，代表登入成功
        logging.info("Login successful")
        return True
    
def run(driver, log_text):
    driver.get(entry_zuvio_url.get())# 輸入課程網址
    time.sleep(3)
    logging.info("STARTING LOOP")
    while True:
        PageSource = driver.page_source # 取得網頁原始碼
        soup = BeautifulSoup(PageSource, 'html.parser')# 解析網頁原始碼
        result = soup.find("div", class_="irs-rollcall")# 尋找點名資訊
        if "準時" in str(result):
            log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M')} 點名完畢")
            return True
        if "簽到開放中" in str(result):
            driver.find_element(By.ID, "submit-make-rollcall").click()
        else:
            log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M')} 無點名資訊")
            driver.refresh()# 重新整理
        time.sleep(random.randint(3, 7))# 隨機等待3~7秒

def on_submit():
    account = entry_account.get()
    password = entry_password.get()
    zuvio_url = entry_zuvio_url.get()
    options = Options()
    options.add_argument('--headless')# 不開啟瀏覽器
    options.binary_location = CHROME_DRIVER_PATH# 
    driver = webdriver.Chrome(options=options)
    login_successful=login(driver, log_text, account, password)
    if login_successful:
        log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M')} - 登入成功\n")# 登入成功
        run(driver,zuvio_url)
    else:
        log_text.insert(tk.END, "登入失敗，無法執行後續操作\n")# 登入失敗
    driver.quit()

root = tk.Tk()
root.title("Zuvio auto roll call")

tk.Label(root, text="Account:").grid(row=0, column=0)
entry_account = tk.Entry(root)
entry_account.grid(row=0, column=1)

tk.Label(root, text="Password:").grid(row=1, column=0)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1)

tk.Label(root, text="Zuvio URL:").grid(row=2, column=0)
entry_zuvio_url = tk.Entry(root)
entry_zuvio_url.grid(row=2, column=1)

submit_button = tk.Button(root, text="Submit", command=on_submit)
submit_button.grid(row=3, column=0, columnspan=2)

log_text = scrolledtext.ScrolledText(root, width=40, height=10, wrap=tk.WORD)
log_text.grid(row=4, column=0, columnspan=2)

status_label = tk.Label(root, text="")
status_label.grid(row=5, column=0, columnspan=2)

root.mainloop()