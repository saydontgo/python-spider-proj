import tkinter as tk
import sys
import threading
from queue import Queue
from io import BytesIO
import base64
from PIL import Image,ImageTk
from tkinter import messagebox
from datetime import datetime
import yuanchuangli
import wenku
import doc88
import docin
import renrendoc
import goldenhoe

submitEvent = threading.Event()  # 用于同步的事件对象
iscreatePopup=threading.Event()   #用于控制弹出验证码窗口
okEvent=threading.Event()            #用于控制告诉子进程弹窗结束
inputQueue=Queue()                     #用于告诉子进程 用户输入的验证码结果
btnActive = False  # 控制按钮是否生效的标志

def createPopup(event):
    def submitBtn(entry, event):
        user_input = entry.get()
        inputQueue.put(user_input)
        input_window.destroy()  # 关闭弹窗
        event.set()
    input_window = tk.Toplevel()
    input_window.title("验证码")
    label = tk.Label(input_window, text="请输入验证码：")
    label.pack(padx=20, pady=10)

    entry = tk.Entry(input_window)
    entry.pack(padx=20, pady=5)

    submit_button = tk.Button(input_window, text="提交",
                              command=lambda :submitBtn(entry, event))
    submit_button.pack(pady=10)

    input_window.grab_set()
def checkEvent():
    if iscreatePopup.is_set():
        iscreatePopup.clear()
        createPopup(okEvent)
    root.after(100,checkEvent)
def onYesSelect():
    global withhead
    withhead=True
    print('程序模式调整为显式爬取')

def onNoSelect():
    global withhead
    withhead=False
    print('程序模式调整为隐式爬取')

def onSubmit():
    """
    提交按钮的回调函数，负责校验输入并触发事件。
    """
    if not btnActive:
        return
    userID = userIDInput.get().strip()
    password = passwdInput.get().strip()

    if not userID or not password:
        messagebox.showerror("错误", "用户名和密码不能为空！")
        return
    global  submitEvent
    submitEvent.set()  # 触发事件，解除某一个线程阻塞
class RedirectOutput:
    """
    自定义类，用于将控制台输出重定向到 Tkinter 的 Text 控件。
    """
    def __init__(self, textWidget):
        self.textWidget = textWidget

    def write(self, message):
        # 在 Text 控件末尾插入消息
        self.textWidget.insert(tk.END, message)
        self.textWidget.see(tk.END)  # 自动滚动到最新内容

    def flush(self):
        # 为了兼容文件描述符的 flush 方法，可以不实现具体逻辑
        pass

def checkPasswd(website):
    print(f'您输入的文档存放于{website}，需要您提供{website}的用户名和密码才有可能下载完全')
    userID = userIDInput.get()
    passwd = passwdInput.get()
    lock.acquire()
    print('请务必确认您的用户名和密码正确，若不正确可能无法下载全文')
    print(f'您的用户名为{userID}')
    print(f'您的密码为{passwd}')
    print('确认无误后点击提交按钮')
    global btnActive
    btnActive = True
    submitButton.config(state="normal")  # 启用按钮
    submitEvent.clear()  # 清除之前的事件，确保可以重新等待
    submitEvent.wait()  # 阻塞，直到用户点击提交按钮
    btnActive = False  # 禁用按钮
    submitButton.config(state="disabled")  # 禁用按钮
    lock.release()

def main():
    url=urlInput.get()
    filepath=filepathInput.get()
    if filepath=='':
        filepath='./'
    if not filepath.endswith('/'):
        filepath+='/'
    global withhead
    my_withhead=withhead  #复制一份防止线程间冲突
    print('下载程序开始')
    if url.find('max.book118') > 0:
        yuan = yuanchuangli.yuanchuangli(url, filepath,my_withhead)
        yuan.main()
    elif url.find('wenku.baidu') > 0:
        checkPasswd('百度文库')
        userID=userIDInput.get()
        passwd=passwdInput.get()
        wenKu = wenku.baiduWenku(url, filepath, userID, passwd, iscreatePopup, okEvent, inputQueue, my_withhead)
        wenKu.main()
    elif url.find('doc88') > 0:
        Doc88 = doc88.Doc88(url, filepath,my_withhead)
        Doc88.main()
    elif url.find('www.docin') > 0:
        checkPasswd('豆丁网')
        userID=userIDInput.get()
        passwd=passwdInput.get()
        Docin = docin.Docin(url, filepath, userID, passwd,my_withhead)
        Docin.main()
    elif url.find('renrendoc') > 0:
        renren = renrendoc.renrendoc(url, filepath,my_withhead)
        renren.main()
    elif url.find('jinchutou.com') > 0:
        gh = goldenhoe.goldenhoe(url, filepath,my_withhead)
        gh.main()
    else:
        print('未识别出文档对应的网站(欢迎告知创作者以补充😃')
        exit(0)

    print('保存成功！')


def  inputChange(event):
    """实时检测输入框内容的变化"""
    if not btnActive:
        return
    global lastInputTime
    currentTime = datetime.now()
    elapsedTime = currentTime - lastInputTime  # 计算运行时长
    lastInputTime = currentTime
    detectDelay=1     #1s延迟
    # 如果最后一次输入时间距离当前时间超过设定的延迟时间，则处理输入
    if elapsedTime.seconds> detectDelay:
        userID = userIDInput.get()
        passwd = passwdInput.get()
        print(f'您的用户名更改为{userID}')
        print(f'您的密码更改为{passwd}')

def clearOutput():
    # 清空输出框
    outputBox.delete("1.0", tk.END)


def start():
    """
    运行下载程序，所有下载程序必须在主线程死亡的时候死亡
    :return:
    """
    # 设置所有进程为守护进程
    thread = threading.Thread(target=main,daemon=True)
    thread.start()

iconData=b"""AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAABAnAAAQJwAAAAAA
AAAAAAD5ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA
+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5
ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFKPnKxXv5ysWb+crFnPnKxZz5ysWc+crFnPnK
xZz5ysWc+crFnPnKxZz5ysWc+crFnPnKxZz5ysWc+crFnPnKxZz5ysWc+crFnPnKxZz5ysWc+crF
nPnKxZz5ysWc+crFnPnKxZv5ysV8+crFKPnKxQD5ysUA+crFAPnKxSv5ysXR+crF//nKxfH5ysXu
+crF7vnKxe75ysXu+crF7vnKxe75ysXu+crF7vnKxe75ysXu+crF7vnKxe75ysXu+crF7vnKxe75
ysXu+crF7vnKxe75ysXu+crF7vnKxe75ysXu+crF8fnKxf/5ysXR+crFK/nKxQD5ysUA+crFevnK
xf/5ysWd+crFLfnKxSv5ysUs/8/JKv/TzSn6y8Yr+crFLPnKxSz5ysUs+crFLPrLxSv/0MMq/9DD
KvrLxSv5ysUs+crFLPnKxSz5ysUs+svGK//TzSn/z8kq+crFLPnKxSv5ysUt+crFnfnKxf/5ysV6
+crFAPnKxQD5ysWL+crF//nKxWX5ysUA+crFANevqwAjISUSMSwvJP///wDqvroA+8zFANeqzgCG
XeQA//+rAAAA/xAAAP8Q//+qAIVd5ADXqs4A+8zFAOq+ugD///8AMSwvJCMhJRLXr6sA+crFAPnK
xQD5ysVl+crF//nKxYv5ysUA+crFAPnKxYv5ysX/+crFZvnKxQA/NzoAPzc6AT83OpA/NzrjPzc6
Qz84NwAjAP8AIwD/BiMA/zojAP+SIwD/0iMA/9IjAP+TIwD/OiMA/wYjAP8APzg3AD83OkM/Nzrj
Pzc6kEE5PAHnvLgA+crFAPnKxWT5ysX/+crFi/nKxQD5ysUA+crFi/nKxf/5ysVm+crFAD42OQA/
NzoAPzc6aj83Ov8/Nzq3Qz8eDCIA/x0jAP+gIwD/7yMA//wjAP/PIwD/zyMA//wjAP/vIwD/oCIA
/x1DPx4MPzc6tz83Ov8/NzpqnIB/APnKxRb5ysVO+crFqPnKxf/5ysWM+crFAPnKxQD5ysWL+crF
//nKxWb5ysUAT0RGAD83OgA/NzoSPzc6vz83Ov0+Nj5jIwD/kiMA//8jAP//IwD/6CMA/10jAP9d
IwD/6CMA//8jAP//IwD/kj42PmM/Nzr9Pzc6wCglKRD9zcg2+crFxfnKxfz5ysX9+crF//nKxYD5
ysUA+crFAPnKxYv5ysX/+crFZvnKxQD5y8UAPzc6AD83OgA/NzpPPzc59z00RekoCd7vIwD/9SMA
/8AjAP/yIwD/8SMA//EjAP/yIwD/wCMA//UoCd7vPTRF6T83Ofc8NDhO/+fhEfnKxcT5ysX9+crF
mvnKxVT5ysVe+crFIfnKxQD5ysUA+crFi/nKxf/5ysVm+crFAPnLxQA/NzoAPzc6AD83Ogg/NzmR
PTNH4CgL2fojAP/qIwD/NCMA/1gjAP/wIwD/8CMA/1gjAP80IwD/6igL2fo9M0fgPzc5kQAAAAT7
y8ZB+crF+vnKxb75ysUM+crFAPnKxQD5ysUA+crFAPnKxQD5ysWL+crF//nKxWb5ysUA+cvFAD43
OgA/NzoAPzc6AERAGQU0IYkjJAH6ziMA/+4jAP8qIwD/FiMA/90jAP/dIwD/FiMA/yojAP/uJAH6
zjQhiSNEQBkF16+rAPnKxUD5ysX5+crFwfnKxQ/5ysUA+crFAPnKxQD5ysUA+crFAPnKxYv5ysX/
+crFZvnKxQD5y8UAPzc6AD83OgA/NzoAQDg1JzsvWF8lBe7cIwD/7SMA/yojAP8YIwD/3iMA/94j
AP8YIwD/KiMA/+0lBe7cOy9YX0A4NSefg4IA+crFEvnKxb75ysX/+crFpfnKxWD5ysVq+crFJvnK
xQD5ysUA+crFi/nKxf/5ysVm+crFAPnLxQA/NzoAPzc6AD83Ohg/NznEPjRE/ykM0/8jAP/vIwD/
NSMA/xgjAP/dIwD/3SMA/xgjAP81IwD/7ykM0/8+NET/Pzc5xD83Ohikh4YA+crFMfnKxbz5ysX5
+crF//nKxf/5ysWD+crFAPnKxQD5ysWL+crF//nKxWb5ysUA8sXAAD83OgA/NzoAPzc6dj83Ov8/
Njy7JwngryMA//8jAP/EIwD/oyMA//MjAP/zIwD/oyMA/8QjAP//Jwngrz82PLs/Nzr/Pzc6dj83
OgDxxL8A+crFEfnKxUP5ysWh+crF//nKxYv5ysUA+crFAPnKxYv5ysX/+crFZvnKxQBKQEIAPzc6
AD83Oik/NzrePzc67UA5NDkfAP8ZIwH8oiUF7/slBPH/IwH97yMB/e8lBPH/JQXv+yMB/KIfAP8Z
QDk0OT83Ou0/NzrePzc6KT02OQD6y8UA+crFAPnKxWT5ysX/+crFi/nKxQD5ysUA+crFi/nKxf/5
ysVk+crFAM2npAA2MDQAPzc6jD83Ov8/NzqQPjVAAjAZpAA4KWwYOi5a1zosYOwtE7lHLRO5Rzos
YOw6LlrXOClsGDAZpAA+NUACPzc6kD83Ov8/NzqMPzc6AD83OgD5ysUA+crFZvnKxf/5ysWL+crF
APnKxQD5ysWL+crF//nKxYr5ysUi/c7IBP/UzwA/NzppPzc6pz83OiI/NzoAQDg1AEA5Mgs/ODi/
Pzg4+EA4NXFAODVxPzg4+D84OL9AOTILQDg1AD83OgA/NzoiPzc6pz83Omk/NzoAPjc6APnKxQD5
ysVm+crF//nKxYv5ysUA+crFAPnKxYn5ysX/+crF/PnKxeb5ysWX+8vGHP///wBAODsFPzc6AD83
OgA/NzoAPzc6AD83OmQ/Nzr8Pzc6/z83Ov8/Nzr8Pzc6ZD83OgA/NzoAPzc6AD83OgA/NzoFPzc6
AT83OgBJP0IA+crFAPnKxWb5ysX/+crFi/nKxQD5ysUA+crFO/nKxZX5ysWL+crFyPnKxf/5ysWm
/MzHCsCdmgA/NzoAPzc6AD83OgA/NzoBPzc6gz83Ov8/Nzq9Pzc6vT83Ov8/NzqDPzc6AT83OgA/
NzoAPzc6AD83OgA/NzoAPzc6APnLxQD5ysUA+crFZvnKxf/5ysWL+crFAPnKxQD5ysUA+crFAPnK
xQD5ysUf+crFzvnKxfT5ysU5+crFAPnKxQAAAAAAPzc6AD83Ogs/Nzq4Pzc63D83Oi4/NzouPzc6
3D83Org/NzoLPzc6AAAAAAAAAAAAAAAAAAAAAAAAAAAA+cvFAPnKxQD5ysVm+crF//nKxYv5ysUA
+crFAPnKxQD5ysUA+crFAPnKxQT5ysW1+crF/PnKxUb5ysUA+crFAAAAAAA/NzoAYEUwADg0PCQx
MT4n/5UAAP+VAAAxMT4nODQ8JGBFMAA/NzoAAAAAAAAAAAAAAAAAAAAAAAAAAAD5y8UA+crFAPnK
xWb5ysX/+crFi/nKxQD5ysUA+crFEfnKxTj5ysUv+crFdfnKxfT5ysXW+crFHvnKxQDxz7gAAAAA
AD83OgD9iAEA/5AAG/+LAHr/iQBM/4kATP+LAHr/kAAb/YgBAD83OgD6ysUA+crFAPnKxQD5ysUA
+crFAPnKxQD5ysUA+crFZvnKxf/5ysWL+crFAPnKxQD5ysV0+crF8/nKxfD5ysX/+crF4fnKxVP5
ysUA+crFAP+JAAD/iQAA/4kAAP+JAAD/iQBC/4kA8f+JAPr/iQD6/4kA8f+JAEL/iQAA/4kAAP9q
AAD5y8gA+crFAPnKxQD5ysUA+crFAPnKxQD5ysVk+crF//nKxYv5ysUA+crFAPnKxYz5ysX/+crF
w/nKxXn5ysUu+crFAPnKxQD5ysUA/4kAAP+JAAL/iQAk/4kAGv+JAAP/iQBJ/4kAkv+JAJL/iQBK
/4kAA/+JABr/iQAk/2gAAfnLyAn5ysVM+crFYvnKxWH5ysVh+crFXvnKxaD5ysX/+crFjPnKxQD5
ysUA+crFi/nKxf/5ysVm+crFAPnKxQD5ysUA+crFAPnJxQD/iQAA/4kAHP+JAM7/iQDP/4kAVf+J
AA//iQAB/4kAAf+JAA//iQBV/4kAz/+JAM7/gAAY+czLN/nKxe75ysX/+crF/vnKxfz5ysX9+crF
//nKxf/5ysV++crFAPnKxQD5ysWL+crF//nKxWb5ysUA+crFAPnKxQAAAAAAAAAAAP+JAAD/iQAJ
/4kAg/+JAPL/iQD7/4kAz/+JAKv/iQCr/4kAz/+JAPv/iQDy/4kAg/9cAAX5y8dC+crF+fnKxc75
ysVd+crFifnKxfL5ysX/+crFsPnKxR/5ysUA+crFAPnKxYv5ysX/+crFZvnKxQD5y8UAAAAAAAAA
AAAAAAAA/4kAAP+JAAD/iQAD/4kAQf+JAJr/iQDS/4kA6P+JAOj/iQDT/4kAm/+JAEH/iQAD+r2e
APnKxUL5ysX6+crFsPnKxTv5ysXL+crF/fnKxZ75ysUW+crFAPnKxQD5ysUA+crFi/nKxf/5ysVl
+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crGAPrEsgD8rGkA9u//AP96ABD/ggAg/4IAIP96ABD1
8f8A/KxpAPrEsgD5ysYA+crFP/nKxff5ysXg+crF4PnKxfz5ysWK+crFDfnKxQD5ysUA+crFAPnK
xQD5ysV1+crF//nKxan5ysU/+crFPfnKxT35ysU9+crFPfnKxT35ysU9+crFPfnKxT35ysY9+cvJ
PPnNzTv5zc07+cvJPPnKxj35ysU9+crFPfnKxTr5ysVv+crF+PnKxf/5ysX0+crFdvnKxQf5ysUA
+crFAPnKxQAAAAAA+crFAPnKxSP5ysXD+crF//nKxfn5ysX3+crF+PnKxfj5ysX4+crF+PnKxfj5
ysX4+crF+PnKxfj5ysX4+crF+PnKxfj5ysX4+crF+PnKxfj5ysX4+crF9/nKxfr5ysX/+crF6vnK
xWL5ysUC+crFAPnKxQD5ysUAAAAAAAAAAAD5ysUA+crFAPnKxRz5ysVm+crFhPnKxYX5ysWF+crF
hfnKxYX5ysWF+crFhfnKxYX5ysWF+crFhfnKxYX5ysWF+crFhfnKxYX5ysWF+crFhfnKxYX5ysWF
+crFhfnKxYP5ysVF+MrIAPnKxQD5ysUA+MnFAAAAAAAAAAAAAAAAAPnKxQD5ysUA+crFAPnKxQD5
ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFAPnK
xQD5ysUA+crFAPnKxQD5ysUA+crFAPnKxQD5ysUA+crFAPnKxAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAgB8AAIAfAACAAAAAAAAAAAAAAAAAAAAGAAAADgAAAAAAAAAAAAAEA
AAADAAAABwAAAA8=
"""

# 创建主窗口
root = tk.Tk()
root.title("文档下载小帮手")  # 窗口标题
iconImage = Image.open(BytesIO(base64.b64decode(iconData)))
iconPhoto = ImageTk.PhotoImage(iconImage)
root.iconphoto(True, iconPhoto)

root.geometry("950x600")  # 窗口大小（宽x高）
# 配置 grid 行列的权重，使得当窗口大小变化时，控件可以响应
root.grid_columnconfigure(0, weight=1)  # 设置第0列的权重
root.grid_columnconfigure(1, weight=10)  # 设置第1列的权重
root.grid_rowconfigure(0, weight=1)  # 设置第0行的权重
root.grid_rowconfigure(1, weight=1)  # 设置第1行的权重
root.grid_rowconfigure(2, weight=1)  # 设置第2行的权重
root.grid_rowconfigure(3, weight=1)  # 设置第3行的权重
root.grid_rowconfigure(4, weight=1)  # 设置第4行的权重
root.grid_rowconfigure(5, weight=5)  # 设置第5行的权重
root.grid_rowconfigure(6, weight=1)  # 设置第6行的权重
width=95
pady=5
withhead=False
tk.Label(root, text="你的url:").grid(row=0, column=0, padx=10, pady=pady, sticky="e")  # 靠右对齐
urlInput = tk.Entry(root, width=width)
urlInput.grid(row=0, column=1, padx=10, pady=pady,sticky='ew')

# 第二行: 左侧是标签，右侧是输入框
tk.Label(root, text="你想存入的位置:").grid(row=1, column=0, padx=10, pady=pady, sticky="e")
filepathInput = tk.Entry(root, width=width)
filepathInput.grid(row=1, column=1, padx=10, pady=pady,sticky='ew')

tk.Label(root, text="用户名（爬取豆丁网或百度文库时需要）:").grid(row=2, column=0, padx=10, pady=pady, sticky="e")
userIDInput = tk.Entry(root, width=width)
userIDInput.grid(row=2, column=1, padx=10, pady=pady,sticky='ew')
userIDInput.bind("<KeyRelease>", inputChange)

tk.Label(root, text="密码（爬取豆丁网或百度文库时需要）:").grid(row=3, column=0, padx=10, pady=pady, sticky="e")
passwdInput = tk.Entry(root, width=width,show='*')
passwdInput.grid(row=3, column=1, padx=10, pady=pady,sticky='ew')
passwdInput.bind("<KeyRelease>", inputChange)

tk.Label(root, text="是否有头（显示爬取过程）:").grid(row=4, column=0, padx=10, pady=pady, sticky="e")
# 定义变量，用于绑定单选框的值
selectedOption = tk.StringVar(value="否")  # 设置默认值

# 创建 "是" 单选框
yesButton = tk.Radiobutton(root, text="是", variable=selectedOption, value="是", command=onYesSelect)
yesButton.grid(row=4, column=1, padx=10, pady=pady, sticky="w")

# 创建 "否" 单选框
noButton = tk.Radiobutton(root, text="否", variable=selectedOption, value="否", command=onNoSelect)
noButton.grid(row=4, column=1, padx=50, pady=pady, sticky="w")

# 创建输出框
outputBox = tk.Text(root, height=25, width=width, bg="lightgrey", state="normal")
outputBox.grid(row=5, column=1, padx=10, pady=pady, sticky="news")
tips="""
温馨提示：

1.该软件暂时不支持批量下载，
但是可以同时下载多个文档；

2.下载多个文档时输出
会比较乱，为正常现象；

3.强烈建议在网络良好的情况下
进行下载，以免失败；

4.本软件仅供爬虫交流学习使用
，请勿商用；

5.本软件支持下载百度文库，
道客巴巴，豆丁，原创力，
人人文库，金锄头文库。

made by saydontgo
"""
tk.Label(root, text=tips).grid(row=5, column=0, padx=10, pady=pady, sticky="n")

# 清空输出按钮
clearButton = tk.Button(root, text="清空输出", command=clearOutput)
clearButton.grid(row=6, column=1, padx=10, pady=pady, sticky="e")

# 开始执行脚本按钮
startButton = tk.Button(root, text="一键开始下载", command=start)
startButton.grid(row=4, column=1, padx=10, pady=pady, sticky="e")

# 提交按钮
submitButton = tk.Button(root, text="提交", command=onSubmit)
submitButton.grid(row=4, column=1, padx=110, pady=pady, sticky="e")
submitButton.config(state="disabled")  # 禁用按钮
# 重定向 sys.stdout 到输出框
sys.stdout = RedirectOutput(outputBox)

lock=threading.Lock()
lastInputTime=datetime.now()
taskQueue=Queue()

checkEvent()

# 运行主循环
root.mainloop()
