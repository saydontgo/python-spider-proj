import basic_tools
import io
import time
from PIL import Image
import requests
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium_tools import getdriver
from list_tool_box import list2set


class renrendoc():

    def __init__(self,url,file_path):
        self.url=url
        self.file_path=file_path
        self.driver,self.wait=getdriver(self.url,5)
        self.title=self.driver.title
        self.totalPages=self.getTotalPages()
        print(f'本文档有{self.totalPages}页')

    def getTotalPages(self):
        return int(re.findall('<span>页数：(.*?)</span>',self.driver.page_source)[0])
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
            except:
                print('网速太慢了，该页下载失败😔')

        img_list[0].save(file_path+pdf_name+'.pdf', "PDF",resolution=100.0,save_all=True, append_images=img_list[1:])

    def openAllPages(self):
        """
        点开所有预览按钮
        :param driver:
        :param wait:
        :return:
        """
        count = 1
        while len(re.findall('全文预览已结束',self.driver.page_source))<1:
            try:
                btn_remain = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[2]/div[2]/div/span[3]')))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_remain)
                print(f'点击第{count}次预览')
                count += 1
                # 强制点击
                self.driver.execute_script("arguments[0].click();", btn_remain)
                time.sleep(0.2)
                del btn_remain
            except Exception:
                print('网速太慢，请重试')
                break
        print('已打开所有预览')

    def scrollToPages(self):
        """
        让所有的图片开始加载，并返回所有页面的图片url列表
        :return:
        """
        time.sleep(3)
        items = self.driver.find_elements(By.CLASS_NAME, "webpreview-item")
        for i, item in enumerate(items):
            print(f'翻到第{i+1}页')
            # 滚动到元素可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", item)
            time.sleep(0.9)
        time.sleep(2)

    def main(self):
        self.openAllPages()
        self.scrollToPages()

        source = self.driver.page_source
        all_pictures=re.findall('src="(//file4\\.renrendoc.*?)"',source)
        all_pictures=list2set(all_pictures)
        self.savePictures(all_pictures,self.file_path,self.title)

if __name__ == '__main__':
    url=input('输入你的url:')
    # file_path=input('输入你想存入的位置：')
    # pdf_name=input('输入保存的pdf名字')
    # timeout=int(input('输入你的timeout'))
    # main(url,file_path,pdf_name,timeout)
    y=renrendoc(url,'./renrendoc/')
    y.main()

