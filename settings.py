path=r'D:\real 科研\招生工程'
primewords=["转专业","调专业"]#固定搜索词汇
threshold=0.7
pieces=5

positive_rate=10#每条QA_data对应正例的比值
negative_rate=5#每条QA_data对应负例的比值
batch_size=16#训练时dataloader的超参数
train_rate=0.7#训练集的占比
