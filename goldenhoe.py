import basic_tools
import io
import time
from PIL import Image
import requests
import re
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium_tools import getdriver
from list_tool_box import list2set


class goldenhoe():

    def __init__(self,url,file_path,withhead):
        self.url=url
        self.file_path=file_path
        self.driver,self.wait=getdriver(self.url,5,withhead)
        self.title=self.driver.title
        self.totalPages=self.getTotalPages()
        print(f'本文档有{self.totalPages}页')

    def getTotalPages(self):
        return int(re.findall('"counts"> / (.*?)</span>',self.driver.page_source)[0])
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
            if total==0:
                print('下载失败😔')
                exit(0)
            print('该文档有付费预览内容，已保存所有预览部分')
        for i,pic in enumerate(pic_list):
            try:
                binnary_data=requests.get(pic, headers=headers).content
                img_list.append(Image.open(io.BytesIO(binnary_data)).convert("RGB"))
                print(f'存入进度：{i+1}/{total}')
            except Exception:
                print(f'网速太慢了，第{i+1}页下载失败😔')
        img_list[0].save(file_path+pdf_name+'.pdf', "PDF",resolution=100.0,save_all=True, append_images=img_list[1:])

    def openAllPages(self):
        """
        点开所有预览按钮
        :return:
        """
        count = 1
        while len(re.findall('下载文档到电脑',self.driver.page_source))>0:
            try:
                btn_remain = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#ntip2 > span > span.fc2e')))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_remain)
                print(f'点击第{count}次预览')
                count += 1
                # 强制点击
                self.driver.execute_script("arguments[0].click();", btn_remain)
                time.sleep(0.2)
                del btn_remain
            except Exception:
                print('已打开所有预览')
                break

    def scrollToPages(self):
        """
        让所有的图片开始加载
        :return:
        """
        try:
            items = self.driver.find_elements(By.CLASS_NAME, "outer_page")
        except TimeoutException:
            print('网速太慢了，下载失败(・∀・(・∀・(・∀・*)')
            return
        for i, item in enumerate(items):
            print(f'翻到第{i+1}页')
            # 滚动到元素可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", item)
            time.sleep(0.2)
        time.sleep(2)

    def main(self):
        self.openAllPages()
        self.scrollToPages()

        source = self.driver.page_source
        all_pictures=re.findall('src="(.*?union.*?goldhoe.com/.*?)"',source)
        all_pictures=list2set(all_pictures)
        self.savePictures(all_pictures,self.file_path,self.title)
        self.driver.quit()


