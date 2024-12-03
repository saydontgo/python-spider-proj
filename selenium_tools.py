from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
def getdriver(url, timeout):
    """
    得到模拟浏览器
    :return:
    """
    options = webdriver.ChromeOptions()
    # options.add_argument(r'--user-data-dir=C:\Users\6666\AppData\Local\Microsoft\Edge\User Data')
    # options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument("--disable-web-security")  # 忽略跨域限制
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver, WebDriverWait(driver, timeout)