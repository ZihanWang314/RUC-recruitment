import requests
from requests import exceptions
from bs4 import BeautifulSoup as bs
import csv
from websites import *
from functools import reduce
import threading
import time
import random
import os

#收集需要爬取的页面

def getsite(url,session,headers):
    try:
        obj=session.get(url,headers=headers[random.randint(0,len(headers)-1)],timeout=0.5)
    except:
        return -1
    if obj.status_code!=200:
        return -1
    else:
        return obj

def concat(x,y):
    if type(x) ==str:
        if type(y) ==str:
            return x+'\n'+y
        else:
            return x
    else:
        if type(y) ==str:
            return y
        else:
            return None 

def getstring(file,error,term=-1,piece=-1,string=-1):
    content=[]
    if term!=-1 and piece != -1:
        site='https://rdzs.ruc.edu.cn'+piece['href']
    else:
        site=string

    A=getsite(site,session,headers)
    if A==-1:
        error.write(term+','+site+'\n')
        error.flush()
        return
    obj=bs(A.text,features="html5lib")
    #第一行:提取并拼接div里的string,第二行:找到可能的div元素
    content=[reduce(concat,[str(j.text) for j in i.find_all('p')+i.find_all('table')]).replace('\xa0','').replace('None','').replace('\n\n','\n') \
        for i in obj.find_all('div') if 'class' in i.attrs.keys() and len(i.attrs['class'])>0 and \
        (i.attrs['class'][0]=='article' or i.attrs['class'][0]=='nc_body') and len(i.find_all('p'))>0]
    if len(content)>0:
        file.writerow([piece['title'],content[0]])
    else:
        
        error.write(site+'\n')
        error.flush()

news=[
    "https://rdzs.ruc.edu.cn/cms/list/rmwd/?tag=1",
    "https://rdzs.ruc.edu.cn/cms/item/?cat=9&parent=1",
    "https://rdzs.ruc.edu.cn/cms/item/?cat=30&parent=7",
    "https://rdzs.ruc.edu.cn/cms/list/rmwd/?tag=3",
    "https://rdzs.ruc.edu.cn/cms/item/?cat=72&parent=1",
    "https://rdzs.ruc.edu.cn/cms/list/ztlm/?cat=34",
    "https://rdzs.ruc.edu.cn/cms/item/?cat=18&parent=4",
    "https://rdzs.ruc.edu.cn/cms/item/?cat=30&parent=7",
    "https://rdzs.ruc.edu.cn/cms/item/?cat=31&parent=7",
]
policies=[
    "https://rdzs.ruc.edu.cn/cms/list/professional/",
    "https://rdzs.ruc.edu.cn/cms/list/rdzz/?cat=16",
    "https://rdzs.ruc.edu.cn/inquiry/enrollplan/indexcms/",
    "https://rdzs.ruc.edu.cn/inquiry/admission/indexcms/",
    "https://rdzs.ruc.edu.cn/inquiry/admission/indexcms/?year=2020",
    "https://rdzs.ruc.edu.cn/inquiry/admission/indexcms/?year=2019",
    "https://rdzs.ruc.edu.cn/inquiry/admission/indexcms/?year=2018",
    "https://rdzs.ruc.edu.cn/cms/index/tslx/",
    ]

headers = [{'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'},
{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
{'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
{'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
{'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)'},
{'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)'},
{'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'},
]
session=requests.Session()
NUM_THREAD=300


#爬取news的网址,存入websites.py
news_dict={}
for url in news:
    print("now crawling "+url+"...")
    A=requests.get(url,headers=headers)
    obj=bs(A.text,features="html5lib")
    name_of_url=obj.find_all('h1')[0].string.replace(" ","").replace("\n","").replace("\t","")
    times=[i for i in obj.strings if "当前共有" in i]
    start=times[0].index("有")+1
    end=times[0].index("篇")
    news_dict.update({name_of_url:{'suburl':[],'url':url,'pages':int(times[0][start:end])}})
    for i in range(1,int((news_dict[name_of_url]['pages']-1)/20)+2):
        A=requests.get(url+'&page='+str(i),headers=headers)
        obj=bs(A.text,features="html5lib")
        news_dict[name_of_url]['suburl']+= [{'title':i.attrs['title'],'href':i.attrs['href']} for i in obj.find_all('ul')[1].find_all('a') if \
            'ztlm' in i.attrs['href'] or \
            'archives' in i.attrs['href'] or \
            ('/cms/item' in i.attrs['href'] and 'html' in i.attrs['href']) \
        ]

with open('websites.py','w+',encoding='utf-8') as f:
    f.write('{\n')
    for i in news_dict.keys():
        f.write("    '"+i+"':"+str(news_dict[i])+',\n')
    f.write('}')


#对网页内容进行爬取,存入招生语料库RUCweb中
for ctime in range(1,5):#循环一定次数,用于多次爬取requests库放弃的网页.第一次使用的时候range设为(5)
    if ctime==0:
        with open('error_sites0.py','w+',encoding='utf-8',newline='') as error:
            for term in list(news.keys())[:-1]:
                filename='PRETRAINING\\data\\招生语料库RUCweb\\'+str(term)+'.csv'
                with open(filename,'a+',encoding='utf-8',newline='') as file:
                    f=csv.writer(file)
                    f.writerow(['新闻标题','新闻内容'])
                    print('now for '+ str(term)+' ..')
                    for i in range(int(len(news[term]['suburl'])/NUM_THREAD)+1):
                        t_list=[]
                        print('now crawling page from '+ str(i*NUM_THREAD+1) + ' to ' + str(min(i*NUM_THREAD+NUM_THREAD,len(news[term]['suburl']))))
                        for j in range(i*NUM_THREAD,min(i*NUM_THREAD+NUM_THREAD,len(news[term]['suburl']))):
                            t=threading.Thread(target=getstring,kwargs={'file':f,'error':error,'piece':news[term]['suburl'][j],'term':term})
                            t_list.append(t)
                            t.start()
                            time.sleep(0.02)
                        for t in t_list:
                            t.join()
    else:
        with open('error_sites'+str(ctime-1)+'.py','r+',encoding='utf-8',newline='') as error,\
            open('error_sites'+str(ctime)+'.py','w+',encoding='utf-8',newline='') as newerror:
            sites=error.readlines()
            t_list=[]
            termnow=''
            file=open('test.py')
            for index,site in enumerate(sites):
                if len(site)>=4 and site[4]==',':
                    if site[:4] != 'termnow':
                        for t in t_list:
                            t.join()
                        t_list=[]
                        termnow=site[:4]
                        file.close()
                        filename='PRETRAINING\\data\\招生语料库RUCweb\\'+str(site[:4])+'.csv'
                        file=open(filename,'a+',encoding='utf-8',newline='')
                    f=csv.writer(file)
                    t=threading.Thread(target=getstring,kwargs={'file':f,'term':site[:4],'error':newerror,'string':site[5:-1]})
                    t.start()
                    time.sleep(0.02)
                    t_list.append(t)
            for t in t_list:
                t.join()   
            file.close()



"""
A=requests.get(url,headers=headers)
for item in bs(A.text).find_all("a"):
    href=item.get("href")
    if "gkxx" in href:
        if href[0] == "/":
            zytb.append(r"https://gaokao.chsi.com.cn"+href)
        else:
            zytb.append(href)
print(zytb)

with open(r'PRETRAINING\data\招生语料库RUCweb'+, 'r+', newline='') as csv_file:
    writer=csv.writer(csv_file)
    writer.writerow(["专业","介绍"])
    for i in range(len(links)):
        tmp=requests.get(links[i]).json()["msg"]
        writer.writerow([tmp["zymc"],tmp["zyjs"]])
        if i%30==0:
            print(i)
"""