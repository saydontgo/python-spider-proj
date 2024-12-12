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
    def __init__(self,url,file_path,userID,passwd,withhead):
        self.url=url
        self.file_path=file_path
        self.userID=userID
        self.passwd=passwd
        self.driver,self.wait=selenium_tools.getdriver(self.url,5,withhead)

    def getTotalPages(self):
        return int(re.findall('"page":"(.*?)"',self.driver.page_source)[0])

    def login(self):
        """
                登录百度文库
                :return:
                """
        loginOuterBtn = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                        '#search-right > div.user-icon-wrap > div > div.user-text')))
        self.driver.execute_script('arguments[0].click()', loginOuterBtn)
        userID = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#TANGRAM__PSP_11__userName')))
        passwd = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#TANGRAM__PSP_11__password')))
        loginInnerBtn = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#TANGRAM__PSP_11__submit')))
        agreeBtn=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#TANGRAM__PSP_11__isAgree')))
        userID.send_keys(self.userID)
        passwd.send_keys(self.passwd)
        time.sleep(1)
        agreeBtn.click()
        time.sleep(1)
        loginInnerBtn.click()
        time.sleep(5)
        try:
            self.driver.find_element(By.CSS_SELECTOR, '#TANGRAM__PSP_11__submit')
            closeBtn = self.driver.find_element(By.CSS_SELECTOR, '#TANGRAM__PSP_4__closeBtn')
            closeBtn.click()
            print('用户名或密码输错，可能只能下载部分文档')
        except:
            pass
        time.sleep(2)
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
            except Exception:
                print('该文档有付费预览内容，已保存所有预览部分')
                break

            print(f'存入进度：{i}/{self.totalPages}')
        if len(img_list)==0:
            print('网速太慢了，下载失败(・∀・(・∀・(・∀・*)')
            exit(0)
        img_list[0].save(self.file_path + self.driver.title+'.pdf', "PDF", resolution=100.0,save_all=True,
                             append_images=img_list[1:])

    def main(self):
        self.totalPages=self.getTotalPages()
        print(f'本文档有{self.totalPages}页')
        self.login()
        self.openAllPages()
        self.saveAllPages()

