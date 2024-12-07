import yuanchuangli
import wenku
import doc88
import docin
import renrendoc
url=input('输入你的url:')
# file_path=input('输入你想存入的位置：')
if url.find('max.book118')>0:
    yuan=yuanchuangli.yuanchuangli(url, './yuanchuangli/')
    yuan.main()
elif url.find('wenku.baidu')>0:
    wenku=wenku.baiduWenku(url, './wendang/')
    wenku.main()
elif url.find('doc88')>0:
    doc88=doc88.Doc88(url,'./doc88/')
    doc88.main()
elif url.find('www.docin')>0:
    print('您输入的文档存放于豆丁网，需要您提供豆丁网的用户名和密码才有可能下载完全')
    userID=None
    passwd=None
    while True:
        userID=input('请输入用户名(手机号/邮箱/用户名)：')
        passwd=input('请输入密码：')
        print('请务必确认您的用户名和密码正确，若不正确将无法下载全文')
        print(f'您的用户名为{userID}')
        print(f'您的密码为{passwd}')
        c=input('是否更改[y/n]')
        if c=='n' or c=='no':
            break
    docin=docin.Docin(url,'./docin/',userID,passwd)
    docin.main()
elif url.find('renrendoc')>0:
    renren=renrendoc.renrendoc(url,'./renrendoc/')
    renren.main()
else:
    print('未识别出文档对应的网站(欢迎告知创作者以补充：)')
    exit(0)

print('保存成功！')



