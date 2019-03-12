#!/usr/bin/python
# coding: utf-8
#jipeng 2017.3.15
#python3将zabbix报警信息发送到微信。
import urllib.request
import json
import sys
import datetime,time
import os
import argparse
import chardet
import requests
import re
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
######################################
#可以访问到zabbix页面的URL
URL = 'http://xxxxxxxxxxxxxxx/zabbix/api_jsonrpc.php'
ZABBIX_URL='http://xxxxxxxxxxxxxxx/zabbix/index.php'
CHART_URL='http://xxxxxxxxxxxxxxx/zabbix/chart.php'
#登录zabbix的账号密码
USERNAME='xxxxxxxxxx'
PASSWORD='xxxxxxxxxxxxx'
#放cookie的路径
COOKIEURL='/usr/lib/zabbix/alertscripts/cookie'
#方式图片的路径
PIC_PATH ='/usr/lib/zabbix/alertscripts/image/'

#微信企业号cat 
corpid ="xxxxxxxxxxxxxxx"
corpsecret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
#配置应用id
appid='1000005'
######################################


#获取上传图片至微信服务器返回的id
def getMediaId(ip,key,auth,USERNAME,PASSWORD,COOKIEURL,ZABBIX_URL,PIC_PATH,CHART_URL,corpsecret,corpid):
	
	###写入cookie文件
	curlcookie='curl  -c %s -b %s -d "name=%s&password=%s&autologin=1&enter=Sign+in" %s '% (COOKIEURL,COOKIEURL,USERNAME,PASSWORD,ZABBIX_URL)
	a=os.system(curlcookie)
	#通过ip获取hostid+graphname进而获取graphids
	hostids=ipgetHostsid(ip,URL,auth)
	hostid=int(hostids[0]['hostid'])
	itemids=getitemid(hostid,key,URL,auth)
	itemid=itemids[0]["itemid"]
	
	###获取一小时前时间
	timedata=datetime.datetime.now()-datetime.timedelta(hours=1)
	stime=timedata.strftime("%Y%m%d%H%M%S")
	
	##保存图片文件
	PIC_URL = "%sgraph.%s.png" % (PIC_PATH,stime)
	curlgraph='curl  -b %s -d "itemids=%s&period=3600&time=%s&width=800" %s >%s'% (COOKIEURL,itemid,stime,CHART_URL,PIC_URL)
	b=os.system(curlgraph)
	
	##上传图片
	tokenURL="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (corpid,corpsecret)
	response = urllib.request.urlopen(tokenURL)
	html = response.read()
	tokeninfo = json.loads(html)
	token = tokeninfo['access_token']
	#获取id
	M_URL="https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=image" % token
	files={'image': open(PIC_URL, 'rb')}
	r =requests.post(M_URL, files=files)
	media_id=json.loads(r.content)
	return media_id["media_id"]
	
#获取微信token
def gettoken(corpsecret,corpid):
    tokenURL="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (corpid,corpsecret)
    token_file = urllib.request.urlopen(tokenURL)
    #token_data = token_file.read()
    token_data = token_file.read().decode('utf-8')
    token_json = json.loads(token_data)
    token_json.keys()
    token = token_json['access_token']
    return token

#发送图文信息	
def senddata(access_token,user,appid,title,content,MEDIA_ID):
    PURL="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+access_token
    send_values = {
        #"touser":user,                          #接收人
        "toparty" : user,                    #部门接收人
        #"totag" : user,                        #标签接收人
        "msgtype":"mpnews",                      #消息类型图文。
        "agentid":appid,                         #微信企业应用id
        "mpnews": {
         "articles":[
                  {
                   "title": title,
                   "thumb_media_id": MEDIA_ID,
                   "author": "zabbix",
                   "content_source_url": ZABBIX_URL,
                   "content":content,
                   "digest": content,
                   "show_cover_pic": "1"
                  },
        ]
                },
	"safe":0
    }
    send_data = json.dumps(send_values)
    send_data = send_data.encode(encoding='UTF8')
    #send_data = json.dumps(send_values, ensure_ascii=False)
    send_request = urllib.request.Request(PURL, send_data)
    response = json.loads(urllib.request.urlopen(send_request).read())

#定义通过HTTP方式访问API地址的函数，后面每次请求API的各个方法都会调用这个函数
def requestJson(URL,values):
        data = json.dumps(values)
        #data = data.encode(encoding='UTF8')
        req = urllib.request.Request(URL, data, {'Content-Type': 'application/json-rpc'})
        response = urllib.request.urlopen(req, data.encode('utf-8'))
        output = json.loads(response.read())
        try:
                message = output['result']
        except:
                message = output['error']['data']
                quit()

        return output['result']

#API接口认证的函数，登录成功会返回一个Token
def authenticate(URL, USERNAME, PASSWORD):
        values = {'jsonrpc': '2.0',
                          'method': 'user.login',
                          'params': {
                                  'user': USERNAME,
                                  'password': PASSWORD
                          },
                          'id': '0'
                          }
        idvalue = requestJson(URL,values)
        return idvalue

#zabbix api通过ip获取主机id
def ipgetHostsid(ip,URL,auth):
	values = {'jsonrpc': '2.0',
			  'method': 'host.get',
			  'params': {
				  'output': [ "host" ], 
				  'filter': {
					  'ip': ip
				  },
			  },
			  'auth': auth,
			  'id': '3'
			  }
	output = requestJson(URL,values)
	return output

#zabbix api 通过hostid获取itemid的函数
def getitemid(hostid,key,URL,auth):
        values = {'jsonrpc': '2.0',
                          'method': 'item.get',
                          'params': {
                                  "output": "itemid",
                                  "hostids": hostid,
                                  "search": {
                                        "key_": key
                                  },
                                  "sortfield": "name",
                          },
                          'auth': auth,
                          'id': '21'
                          }
        output = requestJson(URL,values)
        return output


if __name__ == '__main__':
    auth = authenticate(URL, USERNAME, PASSWORD)
    user = str(sys.argv[1])                  #微信企业号账号标识
    #Partyid = str(sys.argv[1])              #微信企业号部门标识
    #Tagid = str(sys.argv[1])                #微信企业号标签标识
    title = str(sys.argv[2])                 #zabbix传过来的第一个参数-标题
    content = str(sys.argv[3])               #zabbix传过来的第二个参数-内容
    ip=re.findall(r"主机IP:(.+?)<br>",content)[0]#截取ip地址
    key=re.findall(r"告警项目:(.+?)<br>",content)[0]#截取zabbix key
    #获取图片id
    MEDIA_ID=getMediaId(ip,key,auth,USERNAME,PASSWORD,COOKIEURL,ZABBIX_URL,PIC_PATH,CHART_URL,corpsecret,corpid)
    #获取token
    accesstoken = gettoken(corpsecret,corpid)
    #发送图文
    senddata(accesstoken,user,appid,title,content,MEDIA_ID)
