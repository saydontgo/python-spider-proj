from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
def getdriver(url, timeout,withhead:bool):
    """
    得到模拟浏览器
    :return:
    """
    options = webdriver.EdgeOptions()
    if not withhead:
        options.add_argument('--headless')
    options.add_argument("--disable-web-security")  # 忽略跨域限制
    driver = webdriver.Edge(options=options)
    try:
        driver.get(url)
    except Exception as e:
        print('无法打开网页')
        print('未知错误：')
        print(e)
        exit(0)
    return driver, WebDriverWait(driver, timeout)