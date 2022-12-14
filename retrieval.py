#----------https://www.cnblogs.com/morries123/p/8568666.html  GUI设计!!!
import xlrd,csv
import random as rd
import numpy as np
from numpy import random
import pandas as pd
import torch
from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer, util, InputExample, losses, evaluation

from settings import *

q_q_based_model=SentenceTransformer(path+r"\model\query_question_based")
q_a_based_model=SentenceTransformer(path+r"\model\question_answer_based")

def encoding(sentence):
    return q_q_based_model.encode(sentence)+q_a_based_model.encode(sentence)

def QUERY(query,datas):  
    """
    根据query在data中返回对应answer，是demo界面的主要函数
    """
    ret=""
    query_embedding = encoding(str(query)).astype(np.float)

    #datas[i]["_sim"]代表了query和answer的关系
    time=0
    for i in datas:
        time+=1
        passage_embedding = datas[i]["embedding"].astype(np.float)
        datas[i].update({"_sim":util.pytorch_cos_sim(query_embedding, passage_embedding)})

    #排序
    searchlist=sorted(list(datas.values()),key=lambda x:x["_sim"],reverse=True)

    #定义show，展示数据库里的单条qa-pair
    def show(j,showsim=True):
        ret=""
        ret+='Q:'+str(searchlist[j]["query"])+'\n'
        ret+='A:'+str(searchlist[j]["answer"])+'\n'
        ret+=str("\n")
        if showsim==True:
            ret+=str("相似度：%.4f"%(searchlist[j]["_sim"].item()))+'\n'
            ret+=str("\n")
            ret+=str("\n")
        else:
            ret+='\n'
        return ret
        
    #固定匹配词汇
    isprime=0
    for word in primewords:
        if word in query:
            isprime=1
            ret+=str("有关问题：\n")
            for pair in searchlist:
                if word in pair["query"]:
                    ret+=str(pair["query"])
                    ret+=str(pair["answer"])
            ret+=str("\n其他人还搜：\n")
            for j in range(5):
                ret+=show(j,showsim=False)

    #如果没有固定匹配词汇       
    if isprime==0:
        j=0
        while searchlist[j]["_sim"].item()>=threshold and j<=pieces:
            if j==0:
                ret+=str("有关问题：\n")
            ret+=show(j)
            j+=1
        if j==0:
            ret+=str("没有找到相关问题。\n其他人还搜：\n")
            while j<=pieces:
                ret+=show(j,showsim=False)
                j+=1
        elif j>=1:
            ret+=str("\n其他人还搜：\n")
            h=j+1
            while h<=j+pieces:
                ret+=show(h,showsim=False)
                h+=1
        return ret


def retrieval(question,datas):
    returns={}
    if "中法" in question:
        for item in datas:
            if datas[item]["tag"]=="中法学院":
                returns.update({item:datas[item]})
    elif "自招" in question or "自主招生" in question:
        for item in datas:
            if datas[item]["tag"]=="自主招生":
                returns.update({item:datas[item]})
    elif "国家专项" in question or "圆梦计划" in question:
        for item in datas:
            if datas[item]["tag"]=="国家专项和“圆梦计划”":
                returns.update({item:datas[item]})
    else:
        for item in datas:
            if datas[item]["tag"] not in ["中法学院","自主招生","国家专项和“圆梦计划”"]:
                returns.update({item:datas[item]})
    return returns

#########################################################################################################

wb = xlrd.open_workbook(path+r"\PRETRAINING\data\query_answer_pair.xlsx")
sheet_names = wb.sheet_names()
main_datas = dict({})
#按工作簿定位工作表
time=0
for sheet in sheet_names:
    sh = wb.sheet_by_name(sheet)
    for i in range(sh.nrows):
        main_datas.update({time:{"query":sh.row_values(i)[0],"answer":sh.row_values(i)[1],"tag":sheet,
                           }})
        time+=1


with open(path+r"\model\dataset_representation.csv","w+",encoding="utf-8",newline="") as file:
    write=csv.writer(file)
    write.writerow(["id"]+list(range(384)))
    for i in main_datas.keys():
        embedding=encoding(main_datas[i]["query"])
        write.writerow([i]+list(embedding))

df=pd.read_csv(path+r"\model\dataset_representation.csv",header=0,encoding="utf-8")
for i in main_datas.keys():
    main_datas[i].update({"embedding":df[df["id"]==i].values[0][1:]})


#########################################################################################################
#用户输入问题，预处理用户数据并进行输出
if __name__=='__main__':
    while True:
        question=input("请输入您的问题：")
        retrieved_data=retrieval(question,main_datas)
        print(QUERY(question,retrieved_data))
