import basic_tools
import re
import io
import time
from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import base64
import selenium_tools

# 打开目标网页
class baiduWenku():
    def __init__(self,url,file_path):
        self.url=url
        self.file_path=file_path
        self.driver,self.wait=selenium_tools.getdriver(self.url,5)

    def getTotalPages(self):
        return int(re.findall('"page":"(.*?)"',self.driver.page_source)[0])

    def saveCanvas(self,canvas_id):

    # 获取 Canvas 元素的 Base64 数据
        canvas = self.driver.find_element(By.ID,canvas_id)
        # 确保 canvas 元素已正确选择
        # 翻到该页
        self.driver.execute_script("arguments[0].scrollIntoView(true);", canvas)
        time.sleep(1)
        if canvas:
            # 获取 Canvas 元素的 Base64 数据
            canvas_data_url = self.driver.execute_script("""
                var canvas = document.getElementById(arguments[0]);
                var ctx = canvas.getContext('2d');  // 获取 2D 上下文
                if (canvas && canvas.toDataURL) {
                    return canvas.toDataURL('image/png');
                } else {
                    return null;
                }
            """, canvas_id)

            if canvas_data_url:
                # 提取 Base64 编码数据
                canvas_base64 = canvas_data_url.split(',')[1]  # 去掉前缀 'data:image/png;base64,'
                return base64.b64decode(canvas_base64)
            else:
                print("无法获取 Canvas 的数据。")
        else:
            print("未找到 Canvas 元素。")

    def openAllPages(self):
        count = 1
        while True:
            try:
                # time.sleep(100)
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
                time.sleep(2)
                del btn_remain
            except Exception:
                print('已打开所有预览')
                break
    def saveAllPages(self):
        basic_tools.create_dir(self.file_path)
        img_list=[]
        for i in range(1,self.totalPages+1):
            canvas_id='original-creader-canvas-'+str(i)
            try:
                img_list.append(Image.open(io.BytesIO(self.saveCanvas(canvas_id))))
            except :
                print('该文档有付费预览内容，已保存所有预览部分')
                break

            print(f'存入进度：{i}/{self.totalPages}')
        img_list[0].save(self.file_path + self.driver.title+'.pdf', "PDF", save_all=True,
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