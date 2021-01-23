import requests     #发送数据文件
import json         #返回数据转json
import sys          #取文件路径，防止报错
import datetime     #取时间
import random       #取随机体温

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#全局函数
csrf_token="a338ad526e356fa4765a7092789bd718"       #csrf随机生成，防跨站验证
fhcs=""                                             #错误返回代码

#取文本中间函数
def qwb(nr,wb0,wb1):
    wz0=wz1=0
    wz0=nr.find(wb0)+len(wb0)
    wz1=nr.find(wb1,wz0)
    return nr[wz0:wz1]

#发送位置
def fswz(cpi,PHPESSID):
    global fhcs
    url="https://api.uyiban.com/nightAttendance/student/index/signIn?CSRF="+csrf_token
    headers={
        "Cookie":"csrf_token="+csrf_token+";PHPSESSID="+PHPESSID+";cpi="+cpi,
        "User-Agent":"yiban",
        "Origin":"https://c.uyiban.com"
    }
    post={}
    post["Code"]=""
    post["PhoneModel"]=""
    post["SignInfo"]='{"Reason":"","AttachmentFileName":"","LngLat":"103.4488,24.3977","Address":"云南省 红河哈尼族彝族自治州 弥勒市弥阳镇美丽家园"}'
    post["OutState"]="1"
    r = requests.post(url,verify=False,headers=headers,data=post).json()
    return "成功"

#判断访问位置
def fwwz(cpi,PHPESSID):
    global fhcs
    headers={
        "Cookie":"csrf_token="+csrf_token+";PHPSESSID="+PHPESSID+";cpi="+cpi,
        "User-Agent":"yiban",
        "Origin":"https://c.uyiban.com"
    }
    url="https://api.uyiban.com/nightAttendance/student/index/photoRequirements?CSRF="+csrf_token
    requests.get(url,verify=False,headers=headers)
    url="https://api.uyiban.com/nightAttendance/student/index/deviceState?CSRF="+csrf_token
    requests.get(url,verify=False,headers=headers)
    url="https://api.uyiban.com/nightAttendance/student/index/signPosition?CSRF="+csrf_token
    r = requests.get(url,verify=False,headers=headers).json()
    if r["data"]["State"]==0:
        return fswz(cpi,PHPESSID)
    elif r["data"]["State"]==1:
        return "未达签到时段"
    elif r["data"]["State"]==3:
        return "已签到"
    else:
        return "无法提交位置\n\n"+str(r.json())+"\n\n"

#提交表单
def fsbd(post,WFId,cpi,PHPESSID):
    global fhcs
    url="https://api.uyiban.com/workFlow/c/my/apply/"+WFId+"?CSRF="+csrf_token
    headers={
        "Cookie":"csrf_token="+csrf_token+";PHPSESSID="+PHPESSID+";cpi="+cpi,
        "User-Agent":"yiban",
        "Origin":"https://c.uyiban.com"
    }
    post["data"]=str(post["data"]).replace("""'""",'''"''').replace(""" """,'''''')
    post["extend"]=str(post["extend"]).replace("""'""",'''"''').replace(""" """,'''''')
    r = requests.post(url,verify=False,headers=headers,data=post).json()
    if r["code"]==0:
        return "成功"
    else:
        return "失败"

#取反馈ID,取WFId，做post数据
def qfkID(TaskId,cpi,PHPESSID):
    global fhcs
    url="https://api.uyiban.com/officeTask/client/index/detail?TaskId="+TaskId+"&CSRF="+csrf_token
    headers={
        "Cookie":"csrf_token="+csrf_token+";PHPSESSID="+PHPESSID+";cpi="+cpi,
        "User-Agent":"yiban",
        "Origin":"https://c.uyiban.com"
        }
    r = requests.get(url,verify=False,headers=headers).json()
    if r["code"]==0:
        post={}
        post["extend"]={
            "TaskId": TaskId,
            "title": "任务信息",
            "content": [
                {"label": "任务名称", "value": r["data"]["Title"]},
                {"label": "发布机构", "value": r["data"]["PubOrgName"]},
                {"label": "发布人", "value": r["data"]["PubPersonName"]}
            ]
        }
        post["data"]={
            "55e9aaf31b36aada75e4aa84f28827a4": str(round(random.uniform(36.1, 36.9), 1)),
            "8e62115236c4ec05c45daff18a6b0e1c": ["以上都无"],
            "0596b8e5dab5bbc35daea35e46a2fbfa": "好"
        }
        return fsbd(post,r["data"]["WFId"],cpi,PHPESSID)
    else:
        return "取反馈ID失败\n\n"+str(r.json())+"\n\n"

#取签到ID,取TaskId
def qxdID(cpi,PHPESSID):
    global fhcs
    sj=str(datetime.datetime.now().year)+"-"
    sj+=str(datetime.datetime.now().month)+"-"
    sj+=str(datetime.datetime.now().day)
    url="https://api.uyiban.com/officeTask/client/index/uncompletedList?StartTime="+sj+"%2000%3A00&EndTime="+sj+"%2012%3A00&CSRF="+csrf_token
    headers={
        "Cookie":"csrf_token="+csrf_token+";PHPSESSID="+PHPESSID+";cpi="+cpi,
        "User-Agent":"yiban",
        "Origin":"https://c.uyiban.com"
        }
    r = requests.get(url,verify=False,headers=headers).json()
    if r["code"]==0:
        if r["data"]!=[]:
            fhcs="表单签到："+qfkID(r["data"][0]["TaskId"],cpi,PHPESSID)
            fhcs+="\t位置签到："+fwwz(cpi,PHPESSID)
        else:
            fhcs="表单签到：已签到\t位置签到："+fwwz(cpi,PHPESSID)
    else:
        fhcs="签到ID请求失败\n\n"+str(r.json())+"\n\n"

#进校本化，取cpi、PHPESSID
def jxbh(verify_request):
    global fhcs
    url = "https://api.uyiban.com/base/c/auth/yiban?verifyRequest="+verify_request+"&CSRF="+csrf_token
    headers={
        "Cookie":"csrf_token="+csrf_token,
        "User-Agent":"yiban",
        "Origin":"https://c.uyiban.com"
        }
    r = requests.get(url,verify=False,headers=headers,allow_redirects=False)
    if r.json()["code"]==0:
        cpi=qwb(r.headers["Set-Cookie"],"cpi=",";")
        PHPESSID=qwb(r.headers["Set-Cookie"],"PHPSESSID=",";")
        qxdID(cpi,PHPESSID)
    else:
        fhcs="进校本化错误\n\n"+str(r.json())+"\n\n"

#取校本化，取verify_request
def qxbh(access_token):
    global fhcs
    url = "http://f.yiban.cn/iapp/index?act=iapp7463&v="+access_token
    r = requests.get(url,verify=False,allow_redirects=False).headers["Location"]
    if r.count("verify_request=")==1:
        jxbh(qwb(r,"verify_request=","&"))
    else:
        fhcs="取校本化verify_request失败\n\n"+r+"\n\n"

#登录，取access_token
def dl(zh,mm):#zh是账号，mm是密码
    global fhcs#全局化返回参数
    url = "https://mobile.yiban.cn/api/v3/passport/login?mobile="+zh+"&password="+mm+"&imei=0"#登录链接
    headers={#请求头
        "Cookie":"csrf_token="+csrf_token,#防跨站请求，csrf令牌
        "User-Agent":"yiban",#模拟易班请求
        "Origin":"https://c.uyiban.com"#模拟易班请求链接
        }
    r = requests.get(url,verify=False,headers=headers).json()#取返回数据并json化赋值给r
    if r["response"]==100:#判断登录是否成功
        qxbh(r["data"]["user"]["access_token"])#执行取校本化，带access_token参数，access_token是登录令牌
    else:
        fhcs="登录失败\t\t(可能账号或密码错误)\n\n"+str(r)+"\n\n"

#取运行路径并取出账户
lj=sys.argv[0]#取运行路径
wz0=0#路径文本位置
for cs1 in range(lj.count("\\")):#循环到最后一个“\”
    wz0=lj.find("\\",wz0,)+1#寻找wz0位置后面的“\”
lj=lj[0:wz0]#赋值运行路径
with open(lj+'易班账户.txt','r',encoding='utf-8') as f:#取易班用户
    zhmm=f.read()#全部用户赋值给zhmm

 
#拆分账户，账号和密码
for zh_YH in zhmm.split("\n"):#循环输出行，赋值给zh_YH
    if zh_YH=="stop":#停止运行
        break#结束循环，结束运行
    elif zh_YH[0:2]=="//":#注释文本，（只显示，不执行）
        print(zh_YH[2:len(zh_YH)])#显示注释文本
        continue#跳转下一次运行
    elif zh_YH[0:1]=="#":#注释文本，（不显示，不执行）
        continue#跳转下一次运行
    elif zh_YH=="":#空文本，（不显示，不执行）
        continue#跳转下一次运行
    zh_LB=zh_YH.split("---")#把账号分成列表，0是账号，1是密码
    dl(zh_LB[1],zh_LB[2])#登录用户
    print(zh_LB[0]+"\t\t"+fhcs)#输出结果
#完成签到，显示退出
input("\n签到完成，按回车退出")