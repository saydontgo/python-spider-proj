import basic_tools
import re
import base64
import time
from selenium.webdriver import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import selenium_tools

class Doc88:
    def __init__(self,url,file_path,withhead):
        self.url=url
        self.file_path:str=file_path
        self.driver,self.wait=selenium_tools.getdriver(self.url,5,withhead)
        self.totalPages=self.getTotalPages()
        print(f'本文档有{self.totalPages}页')
        print(self.driver.title)

    def getTotalPages(self):
        return int(re.findall('页数：(.*?)\n',self.driver.page_source)[0])

    def openAllPages(self):
        """
        处理滑动验证码，以打开所有页
        :return:
        """
        print('正在试图通过道客巴巴的验证码...')
        try:
            count=1
            while True:
                btn=self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[6]/div/div/div[3]/div[3]/div[2]/div/div/div/div/div[2]/div/div/span')))
                btn.click()
                if count>1:
                    print(f'第{count-1}次尝试失败！')
                print(f'第{count}次尝试...')
                tmp=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#captcha_reading > div > div.safefixed > div.safe-bg')))
                bg_pic=tmp.screenshot_as_png
                slider_pic=base64.b64decode(',iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAMAAADW3miqAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA2ZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDpDREQ0NTFDOTlFOEVFRTExOUFDRDg0MzMwRDY3MEMxMSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpFNjZGOTkzNzhGMjIxMUVFOTU2NEM3NkJDQzAxRTk5NyIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpFNjZGOTkzNjhGMjIxMUVFOTU2NEM3NkJDQzAxRTk5NyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M2IChXaW5kb3dzKSI+IDx4bXBNTTpEZXJpdmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOkQyRDQ1MUM5OUU4RUVFMTE5QUNEODQzMzBENjcwQzExIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkNERDQ1MUM5OUU4RUVFMTE5QUNEODQzMzBENjcwQzExIi8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+z45oLwAAAAlQTFRF////0NDQ////w3BVoAAAAAN0Uk5T//8A18oNQQAAAHhJREFUeNrc1NEKwCAIheG/3v+hRyVtZjovNhg7d8JHlGXURFBFT4woPURIzEZhjVVpNPZ7Regj0ExxwkS+mYoamL+j0dAYyWK3qCnk6kKFeQKfQJmNp1oQI0hcy6uvYD3oHi0tewzBOcEeAvsXyPTryv50Xg4BBgDa0wYkK8ECbgAAAABJRU5ErkJggg==')
                distance=basic_tools.identifyGap(bg_pic,slider_pic)
                basic_tools.performSliderAction(btn,self.driver,distance)
                time.sleep(2)
                count+=1
        except Exception:
            print('成功通过道客巴巴的验证码！')


    def saveAllPages(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "pageContainer")))
            pageNumInput = self.driver.find_element(By.ID, 'pageNumInput')
            print('正在确保所有页面打开...')
            for i in range(self.totalPages):
                pageNumInput.send_keys(Keys.CONTROL, 'a')
                pageNumInput.send_keys(str(i+1))
                pageNumInput.send_keys(Keys.ENTER)
                time.sleep(0.5)
            print('正在保存中...')
            self.driver.execute_script("""
            var keeps = $("#pageContainer").parentsUntil('body').toArray().concat($("#pageContainer").children().toArray())
            var divs = $("div:not(#pageContainer)").toArray()
            divs.filter(x => keeps.indexOf(x) < 0).forEach(x => x.remove())
            """)
        except TimeoutException:
            print('网速太慢了，下载失败(・∀・(・∀・(・∀・*)')
        except Exception as e:
            print('未知错误：')
            print(e)
        self.saveAsPdf()

    def saveAsPdf(self,scale=0.95):
        # 使用 DevTools Protocol 的 printToPDF
        result =self.driver.execute_cdp_cmd("Page.printToPDF", {
            "landscape": False,  # 是否横向打印
            "displayHeaderFooter": False,  # 去除页眉和页脚
            "printBackground": False,  # 打印背景
            "scale": scale,  # 缩放比例
            "preferCSSPageSize": True  # 根据 CSS 控制页边距
        })
        basic_tools.createDir(self.file_path)
        # 将 PDF 数据保存到文件
        with open(self.file_path+self.driver.title+'.pdf', "wb") as f:
            f.write(base64.b64decode(result["data"]))

    def main(self):
        self.openAllPages()
        self.saveAllPages()

# if __name__ == '__main__':
#     doc=Doc88('https://www.doc88.com/p-73247390214211.html?r=1','',withhead=False)
#     doc.main()