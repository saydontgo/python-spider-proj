import basic_tools
import re
import io
import time
import threading
from queue import Queue
from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium_tools

class baiduWenku():
    def __init__(self, url, file_path, userID, passwd, event:threading.Event, resultEvent:threading.Event, inputQueue:Queue, withhead):
        self.url=url
        self.file_path=file_path
        self.userID=userID
        self.passwd=passwd
        self.event=event
        self.resultEvent=resultEvent
        self.inputQueue=inputQueue
        self.driver,self.wait=selenium_tools.getdriver(self.url,5,withhead)

    def getTotalPages(self):
        return int(re.findall('"page":"(.*?)"',self.driver.page_source)[0])
    def handleVerification(self):
        verifybtn = self.driver.find_element(By.CSS_SELECTOR, '#goToVerify')
        verifybtn.click()
        time.sleep(2)
        codeInput = self.driver.find_element(By.CSS_SELECTOR, '#passAuthVcode')
        self.event.set()
        self.resultEvent.wait()
        codeInput.send_keys(self.inputQueue.get())
        nextstep=self.driver.find_element(By.CSS_SELECTOR, '#passAuthSubmitCode')
        nextstep.click()
        self.driver.save_screenshot("debug_screenshot3.png")
    def login(self):
        """
        登录百度文库
        :return:
        """
        try:
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
        except:
            print('页面没有加载完全,下载失败')
            self.driver.quit()
            exit(0)
        time.sleep(5)
        try:
            self.driver.find_element(By.CSS_SELECTOR, '#TANGRAM__PSP_11__submit')
            closeBtn = self.driver.find_element(By.CSS_SELECTOR, '#TANGRAM__PSP_4__closeBtn')
            closeBtn.click()
            print('用户名或密码输错，可能只能下载部分文档')
        except:
            try:
                self.handleVerification()
            except Exception as e:
                print(e)
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
            self.driver.quit()
            exit(0)
        img_list[0].save(self.file_path + self.driver.title+'.pdf', "PDF", resolution=100.0,save_all=True,
                             append_images=img_list[1:])

    def main(self):
        self.totalPages=self.getTotalPages()
        print(f'本文档有{self.totalPages}页')
        self.login()
        self.openAllPages()
        self.saveAllPages()
        self.driver.quit()

