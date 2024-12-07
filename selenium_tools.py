from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
def getdriver(url, timeout):
    """
    得到模拟浏览器
    :return:
    """
    options = webdriver.EdgeOptions()
    options.add_argument('--headless')
    options.add_argument("--disable-web-security")  # 忽略跨域限制
    driver = webdriver.Edge(options=options)
    driver.get(url)
    return driver, WebDriverWait(driver, timeout)