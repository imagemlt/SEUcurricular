#!/usr/bin/env python
#coding=utf-8
import urllib2
import urllib
import cookielib
import re
from bs4 import BeautifulSoup

#函数列表：
# getopener()获取表单信息与储存有cookies等的openner;
# getTable(a,y="")获取网页内容
#getStuinfo(bs1)提取学生信息
#getClasses(bs1)获取班级信息
#getTimetable(bs1)获取课程表

def getopener():
	"此函数用于获取保存了cookies的opener与表单数据"
	cookies=cookielib.MozillaCookieJar()
	opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
	request=urllib2.Request("http://xk.urp.seu.edu.cn/jw_service/service/lookCurriculum.action")
	request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) Gecko/20080404 (FoxPlus) Firefox/2.0.0.14')
        try:
            ans=opener.open(request,timeout=10)
            bs1=BeautifulSoup(ans.read(),"lxml")
        except urllib2.URLError,e:
            print "连接错误，请检查是否已接入seu内网。错误原因："+str(e.reason)
            exit()
        return opener,ans,bs1

def getTable(a,y=""):
	"此函数用于获取网页内容"
	opener,response,bs1=getopener()
	'处理表单数据'
	datas={}
	for i in bs1.findAll('input'):
	    if i.has_attr('value') and i.has_attr('name'):
		datas[i.attrs['name']]=i.attrs['value'].encode('utf-8')
	datas['queryStudentId']=a
	'处理表单中的select'
        if y=="":
	    for m in bs1.findAll('select'):
	        print "输入学年选择:"
	        codec=0
	        l=[]
	        for n in m.findAll('option'):
		        print "%d.=>%s  "%(codec,n.text),
		        l.append(n.string)
		        codec=codec+1
	        choice=int(raw_input("\n输入你选择的序号:"))
	        datas[m.attrs['name']]=l[choice]
        else:
            datas['queryAcademicYear']=y
            print datas
	request=urllib2.Request("http://xk.urp.seu.edu.cn/jw_service/service/stuCurriculum.action",data=urllib.urlencode(datas))
	request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) Gecko/20080404 (FoxPlus) Firefox/2.0.0.14')
	bs1=BeautifulSoup(opener.open(request).read(),'lxml')
	content=bs1.prettify().encode("utf-8")
	if "没有找到" in content:
		return None
	return bs1

def getStuinfo(bs1):
	"此函数用于提取学生个人信息"
	stuinfotb=bs1.findAll('table')[4].findAll('td')
	stuinfo={}
	for i in stuinfotb:
	    key,value=i.text.split(':')
	    key=re.sub(r'[\s|\xa0]+','',key)
	    stuinfo[key]=value
	return stuinfo

def getClasses(bs1):
	"此函数用于提取课程信息"
	calssestb=bs1.findAll('table')[6]
	classes=[]
	columns=[]
	begin=0
	total=0.0
	for i in calssestb.findAll('tr'):
	    if begin is 0:
		for m in i.findAll('td'):
		    columns.append(re.sub(r'[\s|\xa0]+','',m.text))
		    begin=1
	    else:
		perclass={}
		beginpos=0
		sig=True
		for m in i.findAll('td'):
		    if re.match(r'^[\xa0]*$',m.text):
		            find1=False
		            for n in i.findAll('td'):
		                if  re.sub(r'^[\s|\xa0]+$','',n.text)==u"合计":
		                    find1=True
		                    continue
		                if find1 and not re.match(r'^[\xa0]*$',n.text):
		                    total=float(re.sub(r'[\s|\xa0]+','',n.text))
		            sig=False
		            break
		    if columns[beginpos]==u"学分":
		        perclass[columns[beginpos]]=float(re.sub(r'[\s|\xa0]+','',m.text))
		    else:
		        perclass[columns[beginpos]]=re.sub(r'[\s|\xa0]+','',m.text)
		    beginpos=beginpos+1
		if sig:
		    classes.append(perclass)
	return classes,total

def getTimetable(bs1):
	"此函数用于获取时间表"
	roll=[8,9,10,11,12,19,20,21,22,23,30,31,32,33,34,37,39,41]
	tb=bs1.findAll("table")[7]
	timetable={}
	i=0
	for  m in tb.select('.line_topleft'):
		dealed=m.get_text(separator="\t",strip=True)
		match=re.match(ur'(\S*?)\t\[(\d)+\-(\d+)周\](\d+)\-(\d+)节\t*(\S*)',dealed)                                                         #匹配课程信息
		if match is not None:
                        timetable[i]=re.findall(ur'(\S*?)\t\[(\d)+\-(\d+)周\](\d+)\-(\d+)节\t*(\S*)',dealed)
		else:
			if i in roll and i !=41:
				timetable[i]=[]
			if i==41:
				timetable[i]=re.sub('\t','\n',dealed)
		i=i+1
	return timetable

def main():
	a=str(raw_input('输入您的学号：'))
	bs1=getTable(a)
        if bs1 is None:
            print "查询失败!"
            exit()
	stuinfo=getStuinfo(bs1)
	classes,total=getClasses(bs1)
	timetable=getTimetable(bs1)
	print "#####################个人信息#########################"
	for key in stuinfo:
	    print key+"=>"+stuinfo[key]

	print "####################选课信息###########################"
	for m in classes:
	    print '----------------------------------------------------'
	    for n in m:
		if n==u"学分":
		    print n+"=>"+str(m[n]),
		else:
		    print n+"=>"+m[n],
	    print
	print "\n总学分：%.1f"%total

	print "####################时间安排##############################"
	roll=[(8,"星期一上午"),(9,"星期二上午"),(10,"星期三上午"),(11,"星期四上午"),(12,"星期五上午"),(19,"星期一下午"),(20,"星期二下午"),(21,"星期三下午"),(22,"星期四上午"),(23,"星期五下午"),(30,"星期一晚"),(31,"星期二晚"),(32,"星期三晚"),(33,"星期四晚"),(34,"星期五晚"),(37,"星期六"),(39,"星期日"),(41,"备注")]
	for (key,value) in roll:
	    print '=============='
	    print value+":"
	    if key!=41:
		for n in timetable[key]:
		    print '---------------'
		    for (x,y) in zip([u"课程名称",u"开始周次",u"结束周次",u"开始课次",u"结束课次",u"上课地点"],n):
		        print x+"=>"+y
		    print '\n----------------'
	    else:
		print timetable[key]

if __name__=="__main__":
	main()
