# 2021 RUC RECRUITMENT QUESTION-ANSWERING SYSTEM

<b>2021 RUC-RecQA. Program is halted, this respiratory is for backup only.</b>


The file PRETRAINING shows the process of fine-tuning the model
from "bert-base-chinese", including:
    (1)using the corpus from 
        https://gaokao.chsi.com.cn/ 
        which is national official recruitment website, with 
        Masked-Language-Model to fine-tune the model's word
        embeddings.
    (2) using the query-answer pairs from
        query_answer_pair.xlsx and 
        data_augmentation.xlsx
        by sentence-transformer to fine-tune the model's ability
        of matching relative sentences.
    (3) using the dataset of
        CLUE and CMRC2018, to improve the model's ability of
        extracting information from documents.
    (4) using the dataset of 
        https://rdzs.ruc.edu.cn/cms/
        which is RUC official recruitment website, to amplify the 
        query set of the model.



