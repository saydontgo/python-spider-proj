import basic_tools
import re
import io
import time
from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium_tools

# 打开目标网页
class baiduWenku():
    def __init__(self,url,file_path):
        self.url=url
        self.file_path=file_path
        self.driver,self.wait=selenium_tools.getdriver(self.url,5)

    def getTotalPages(self):
        return int(re.findall('"page":"(.*?)"',self.driver.page_source)[0])

    def openAllPages(self):
        count = 1
        while True:
            try:
                btn_remain = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.unfold, .read-all')))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_remain)
                print(f'点击第{count}次预览')
                count += 1
                # 强制点击
                self.driver.execute_script("arguments[0].click();", btn_remain)
                try:
                    self.driver.find_element(By.CLASS_NAME,'pc-vip-cashier-dialog')
                    print('已打开所有预览')
                    break
                except:
                    pass
                time.sleep(0.5)
                del btn_remain
            except Exception:
                print('已打开所有预览')
                break
    def saveAllPages(self):
        basic_tools.createDir(self.file_path)
        img_list=[]
        for i in range(1,self.totalPages+1):
            canvas_id='original-creader-canvas-'+str(i)
            try:
                img_list.append(Image.open(io.BytesIO(basic_tools.saveCanvas(self.driver,self.wait,canvas_id))))
            except Exception as e:
                print(e)
                print('该文档有付费预览内容，已保存所有预览部分')
                break

            print(f'存入进度：{i}/{self.totalPages}')
        img_list[0].save(self.file_path + self.driver.title+'.pdf', "PDF", resolution=100.0,save_all=True,
                             append_images=img_list[1:])

    def main(self):
        self.totalPages=self.getTotalPages()
        print(f'本文档有{self.totalPages}页')
        self.openAllPages()
        self.saveAllPages()

if __name__ == '__main__':
    url=input('输入你的url：')
    bw=baiduWenku(url,'./wendang/')
    bw.main()