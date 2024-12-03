import yuanchuangli
import wenku

url=input('输入你的url:')
# file_path=input('输入你想存入的位置：')
if url.find('max.book118')>0:
    yuan=yuanchuangli.yuanchuangli(url, './yuanchuangli/')
    yuan.main()
elif url.find('wenku.baidu')>0:
    wenku=wenku.baiduWenku(url, './wendang/')
    wenku.main()
else:
    print('未识别出文档对应的网站(欢迎告知创作者以补充：)')
    exit(0)

print('保存成功！')



