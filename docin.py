from basic_tools import elements
import basic_tools
from list_tool_box import list2set
import re
import requests
import io
import time
from PIL import Image
from selenium.webdriver import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium_tools

# 打开目标网页
class Docin():
    def __init__(self,url,file_path,userID,passwd,withhead):
        self.url=url
        self.file_path=file_path
        self.timeout=20
        self.userID=userID
        self.passwd=passwd
        self.driver,self.wait=selenium_tools.getdriver(self.url,self.timeout,withhead)

    def getTotalPages(self):
        return int(re.findall('<span>(.*?)</span>页',self.driver.page_source)[0])

    def login(self):
        """
        登录豆丁网
        """
        loginOuterBtn=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.head_wrapper > div > div.top_nav_wrap > div.nav_end_bd.nav_end_sty2 > div.top_nav_item > ul > li:nth-child(3) > a')))
        self.driver.execute_script('arguments[0].click()',loginOuterBtn)
        userID=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#username_new')))
        passwd=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#password_new')))
        loginInnerBtn=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#loginnew > div.loginSubmitBtn > a.btn.loginBtn')))

        userID.send_keys(self.userID)
        passwd.send_keys(self.passwd)
        time.sleep(1)
        loginInnerBtn.click()
        time.sleep(10)
        try:
            self.driver.find_element(By.CSS_SELECTOR,'#loginnew > div.loginSubmitBtn > a.btn.loginBtn')
            closeBtn=self.driver.find_element(By.CSS_SELECTOR,'#newlogin > span')
            closeBtn.click()
            print('用户名或密码输错，只能下载部分文档')
        except:
            pass
        time.sleep(2)

    def savePictures(self,pic_list:list,file_path,pdf_name):
        """
        将传入的照片url的照片存入固定文件夹
        :param pic_list:
        :return:
        """
        headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
        }
        basic_tools.createDir(file_path)
        img_list=[]
        total=len(pic_list)
        if total<self.totalPages:
            print('该文档有付费预览内容，已保存所有预览部分')
        for i,pic in enumerate(pic_list):
            try:
                binnary_data=requests.get('https:' + pic, headers=headers).content
                img_list.append(Image.open(io.BytesIO(binnary_data)).convert("RGB"))
                print(f'存入进度：{i+1}/{total}')
            except TimeoutError:
                print(f'网速太慢了，第{i+1}页下载失败😔')
        img_list[0].save(file_path+pdf_name+'.pdf', "PDF",resolution=100.0,save_all=True, append_images=img_list[1:])

    def saveSpecialPages(self):
        try:
            items = self.driver.find_elements(By.CSS_SELECTOR, ".model.panel.scrollLoading")
            for i, item in enumerate(items):
                print(f'翻到第{i+1}页')
                # 滚动到元素可见
                self.driver.execute_script("arguments[0].scrollIntoView(true);", item)
                time.sleep(0.5)
        except EC.NoSuchElementException:
            print('网速太慢了，下载失败(・∀・(・∀・(・∀・*)')
        except Exception as e:
            print('未知错误：')
            print(e)
        source = self.driver.page_source
        all_pictures = re.findall('<img.*?onload.*?src="https:(.*?)">', source)
        all_pictures = list2set(all_pictures)
        self.savePictures(all_pictures, self.file_path, self.driver.title)
    def saveAllPages(self):
        basic_tools.createDir(self.file_path)
        img_list=[]
        if len(re.findall('超出预览范围',self.driver.page_source))>0:
            self.saveSpecialPages()
            return

        self.login()
        try:
            contBtn = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'model-fold-show')))
        except:
            print('可能触发豆丁网的登录滑动验证机制，需要打开有头并手动通过验证码')
            exit(0)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", contBtn)
        time.sleep(2)
        self.driver.execute_script("arguments[0].click();", contBtn)
        time.sleep(2)

        try:
            inputKey=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#page_cur')))
        except TimeoutException:
            print('网速太慢了，下载失败(・∀・(・∀・(・∀・*)')
            return
        inputKey.send_keys(Keys.CONTROL, 'a')
        inputKey.send_keys('2')
        inputKey.send_keys(Keys.ENTER)
        time.sleep(2)
        for i in range(1,self.totalPages+1):
            inputKey.send_keys(Keys.CONTROL, 'a')
            inputKey.send_keys(str(i))
            inputKey.send_keys(Keys.ENTER)
            canvas_CSS=f'#img_{str(i)} > div > div > div > canvas'
            try:
                img_list.append(Image.open(io.BytesIO(basic_tools.saveCanvas(self.driver,self.wait,canvas_CSS,elements.CSS))))
            except Exception:
                print('正在保存已下载部分...')
                print('无法继续下载，有以下可能原因：')
                print('1.您未成功登录')
                print('2.豆丁网有限制普通用户一定时间内查看完整文章的次数，请先检查手动点击继续阅读是否能打开全文，若不能打开，请等待次数冷却后再次尝试')
                print(f'3.网速过慢，本软件设置的timeout为{self.timeout}s，超过{self.timeout}s时间页面未加载自动停止加载')
                break

            print(f'存入进度：{i}/{self.totalPages}')
        if len(img_list)==0:
            print('下载失败😔')
            exit(0)
        img_list[0].save(self.file_path + self.driver.title+'.pdf', "PDF", resolution=100.0,save_all=True,
                             append_images=img_list[1:])

    def main(self):
        self.totalPages=self.getTotalPages()
        print(f'本文档有{self.totalPages}页')
        self.saveAllPages()
        self.driver.quit()

# if __name__ == '__main__':
#     doc=Docin('https://www.doc88.com/p-73247390214211.html?r=1','',withhead=False)
#     doc.main()