import xlrd
import random as rd
import numpy as np
from numpy import random
import csv


from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation

from settings import *

#########################################################################################################
print("""读取问答数据并形成main_datas,数据结构为{id:{"query":..,"answer":...,"tag":...,},}""")

wb = xlrd.open_workbook(r"PRETRAINING\data\query_answer_pair.xlsx")
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

#########################################################################################################
print("""读取data_augmentation,xlsx中的非空元素并形成aug_datas，数据结构为[[sen11,sen12,...],[sen21,sen22,...],]""")

wb = xlrd.open_workbook(r"PRETRAINING\data\data_augmentation.xlsx")
sheet_names = wb.sheet_names()

aug_datas=[]
foo=[]
for sheet in sheet_names:
    sh = wb.sheet_by_name(sheet)
    for i in range(sh.nrows):
        foo.append([])
        for j in sh.row_values(i):
            if j != "":
                foo[i].append(j)
for i in foo:
    if len(i)!=0:
        aug_datas.append(i)

                
#########################################################################################################
print("""预训练Query-Questions匹配模型""")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

#生成训练数据
train_examples=[]
for i in range(len(aug_datas)):
    #生成正样本
    if len(aug_datas[i])!=1:
        for j in range(positive_rate):
            r1,r2=rd.sample(range(len(aug_datas[i])),2)
            train_examples.append(InputExample(texts=[aug_datas[i][r1],aug_datas[i][r2]],label=1.0))
    #生成负样本
    for j in range(5):
        false_index=random.randint(len(aug_datas))
        while false_index==i:
            false_index=random.randint(len(aug_datas))
        false_num=random.randint(len(aug_datas[false_index]))
        train_examples.append(InputExample(texts=[aug_datas[i][0],aug_datas[false_index][false_num]],label=0.0))
#生成训练集
shuffle_num=int(len(train_examples)*train_rate)
shuffled_train_examples=[]
shufflelist=random.permutation(len(train_examples))
for i in range(len(train_examples)):
    shuffled_train_examples.append(train_examples[shufflelist[i]])
train_dataloader = DataLoader(shuffled_train_examples[:shuffle_num], shuffle=True, batch_size=batch_size)
train_loss = losses.CosineSimilarityLoss(model)
#生成测试集
sentences1 = []
sentences2 = []
scores = []
for pair in shuffled_train_examples[shuffle_num:]:
    sentences1.append(pair.texts[0])
    sentences2.append(pair.texts[1])
    scores.append(pair.label)
evaluator = evaluation.EmbeddingSimilarityEvaluator(sentences1, sentences2, scores)

model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=3, warmup_steps=100, evaluator=evaluator, evaluation_steps=500, save_best_model=True)
model.save(r"model\query_question_based")
                
#########################################################################################################
print("""预训练Questions-Answer匹配模型""")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
train_examples=[]
for i in main_datas.keys():
    for j in range(positive_rate):
        train_examples.append(InputExample(texts=[main_datas[i]["query"],main_datas[i]["answer"]],label=1.0))   
    for j in range(negative_rate):
        false_index=random.randint(len(main_datas))
        while false_index==i:
            false_index=random.randint(len(main_datas))
        train_examples.append(InputExample(texts=[main_datas[i]["query"],main_datas[false_index]["answer"]],label=0.0))
#生成训练集
shuffle_num=int(len(train_examples)*train_rate)
shuffled_train_examples=[]
shufflelist=random.permutation(len(train_examples))
for i in range(len(train_examples)):
    shuffled_train_examples.append(train_examples[shufflelist[i]])
train_dataloader = DataLoader(shuffled_train_examples[:shuffle_num], shuffle=True, batch_size=batch_size)
train_loss = losses.CosineSimilarityLoss(model)
#生成测试集
sentences1 = []
sentences2 = []
scores = []
for pair in shuffled_train_examples[shuffle_num:]:
    sentences1.append(pair.texts[0])
    sentences2.append(pair.texts[1])
    scores.append(pair.label)
evaluator = evaluation.EmbeddingSimilarityEvaluator(sentences1, sentences2, scores,write_csv=True)

model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=3, warmup_steps=100, evaluator=evaluator, evaluation_steps=500, save_best_model=True)
model.save(r"model\question_answer_based")

#########################################################################################################
print("""根据预训练后的模型生成main_datas中数据的sentence_embedding""")
q_q_based_model=SentenceTransformer('model\query_question_based')
q_a_based_model=SentenceTransformer('model\question_answer_based')
def encoding(sentence):
    return q_q_based_model.encode(sentence)+q_a_based_model.encode(sentence)

with open(r"model\dataset_representation.csv","w+",encoding="utf-8",newline="") as file:
    write=csv.writer(file)
    write.writerow(["id"]+list(range(384)))
    for i in main_datas.keys():
        embedding=encoding(main_datas[i]["query"])
        write.writerow([i]+list(embedding))


