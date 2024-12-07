import os
from enum import Enum
import time
import cv2
import numpy as np
import random
import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

class elements(Enum):
    ID=1
    CSS=2
    XPATH=3
    CLASSNAME=4
def createDir(path: str):
    """
    若不存在传入的path，就创建目录
    """
    if not os.path.exists(path):
        os.makedirs(path)

def saveCanvas(driver,wait,canvasX,mode=elements.ID):
# 获取 Canvas 元素的 Base64 数据
    if mode==elements.ID:
        canvas = wait.until(EC.presence_of_element_located((By.ID,canvasX)))
    elif mode==elements.CSS:
        canvas=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,canvasX)))
    elif mode==elements.XPATH:
        canvas=wait.until(EC.presence_of_element_located((By.XPATH,canvasX)))
    elif mode==elements.CLASSNAME:
        canvas=wait.until(EC.presence_of_element_located((By.CLASS_NAME,canvasX)))
    else:
        print('传入模式不合法!')
        return
    # 确保 canvas 元素已正确选择
    # 翻到该页
    driver.execute_script("arguments[0].scrollIntoView(true);", canvas)
    time.sleep(0.3)
    if canvas:
        # 获取 Canvas 元素的 Base64 数据
        canvas_data_url = driver.execute_script("""
            canvas=arguments[0]
            var ctx = canvas.getContext('2d');  // 获取 2D 上下文
            if (canvas && canvas.toDataURL) {
                return canvas.toDataURL('image/png');
            } else {
                return null;
            }
        """, canvas)

        if canvas_data_url:
            # 提取 Base64 编码数据
            canvas_base64 = canvas_data_url.split(',')[1]  # 去掉前缀 'data:image/png;base64,'
            return base64.b64decode(canvas_base64)
        else:
            print("无法获取 Canvas 的数据。")
    else:
        print("未找到 Canvas 元素。")

def performSliderAction(slider,driver,distance):
    action = ActionChains(driver)
    action.click_and_hold(slider)  # 按住滑块
    action.pause(0.2)  # 模拟人类操作的短暂停顿

    # 生成随机轨迹
    tracks = generateTrack(distance)

    for track in tracks:
        action.move_by_offset(xoffset=track, yoffset=0)  # 按轨迹移动
        action.pause(random.uniform(0.01, 0.02))  # 每次移动间隔随机化，模拟人类行为

    action.release().perform()  # 松开鼠标

# 生成滑动轨迹
def generateTrack(distance):
    """
    生成模拟人类操作的滑动轨迹。
    :param distance: 滑动总距离
    :return: 每次滑动的距离列表
    """
    tracks = []
    current = 0
    mid = distance * 3 / 4  # 前段加速，中段匀速，后段减速
    while current < distance:
        if current < mid:
            # 加速阶段
            move = random.randint(15, 20)
        else:
            # 减速阶段
            move = random.randint(13, 15)

        current += move
        if current > distance:
            move -= (current - distance)
            current = distance

        tracks.append(move)
    return tracks


def identifyGap(bg, tp):
    '''
    bg: 背景图片的数据流
    tp: 缺口图片的数据流

    该函数返回最佳匹配的缺口左上角的x水平坐标
    '''
    # 读取背景图片和缺口图片

    img_array = np.frombuffer(bg, dtype=np.uint8)
    img_array_slider = np.frombuffer(tp, dtype=np.uint8)
    # 用 OpenCV 解码为图像
    bg_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    tp_img = cv2.imdecode(img_array_slider, cv2.IMREAD_COLOR)

    # 识别图片边缘
    bg_edge = cv2.Canny(bg_img, 100, 200)
    tp_edge = cv2.Canny(tp_img, 100, 200)

    # 转换图片格式
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

    # 缺口匹配
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配

    # 返回缺口的X坐标
    return max_loc[0]